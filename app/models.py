"""Modelo de datos (SQLAlchemy 2.0)."""
from __future__ import annotations

import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- Enumeraciones ------------------------------------------------------------


class SubjectKind(str, enum.Enum):
    person = "person"
    company = "company"


class SubscriptionStatus(str, enum.Enum):
    incomplete = "incomplete"
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"
    unpaid = "unpaid"


class SourceScope(str, enum.Enum):
    estatal = "estatal"
    autonomico = "autonomico"
    provincial = "provincial"


class MatchType(str, enum.Enum):
    identifier = "identifier"  # coincidencia por DNI/NIE/CIF (alta precisión)
    name = "name"              # coincidencia por nombre (requiere revisión)


# --- Usuarios y suscripción ---------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255), default="")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Consentimiento RGPD (obligatorio en el registro)
    accepted_terms_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    consent_self_data: Mapped[bool] = mapped_column(Boolean, default=False)

    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    subjects: Mapped[list["Subject"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscription: Mapped["Subscription | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def has_active_subscription(self) -> bool:
        s = self.subscription
        return bool(s and s.status in (SubscriptionStatus.active, SubscriptionStatus.trialing))


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.incomplete
    )
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="subscription")


class Subject(Base):
    """Identidad vigilada: la persona o empresa cuyos datos monitoriza el usuario.

    Clave legal: el usuario declara ser el titular del dato o su representante
    autorizado. Solo se vigilan datos propios o consentidos.
    """

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[SubjectKind] = mapped_column(Enum(SubjectKind), default=SubjectKind.person)

    display_name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255), index=True)

    identifier: Mapped[str | None] = mapped_column(String(32))          # tal cual lo introdujo
    normalized_id: Mapped[str | None] = mapped_column(String(32), index=True)
    id_kind: Mapped[str | None] = mapped_column(String(8))              # DNI/NIE/CIF

    # ¿El titular es el propio usuario o un tercero autorizado?
    is_self: Mapped[bool] = mapped_column(Boolean, default=True)
    consent_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    active: Mapped[bool] = mapped_column(Boolean, default=True)
    monitor_name: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="subjects")
    matches: Mapped[list["Match"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


# --- Boletines y publicaciones ------------------------------------------------


class Source(Base):
    """Un diario/boletín oficial seguido (BOE, BORME, autonómico, provincial...)."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    scope: Mapped[SourceScope] = mapped_column(Enum(SourceScope), default=SourceScope.estatal)
    region: Mapped[str] = mapped_column(String(128), default="")
    homepage: Mapped[str] = mapped_column(String(255), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Adaptador de ingesta implementado actualmente (true) o pendiente (false).
    implemented: Mapped[bool] = mapped_column(Boolean, default=False)

    publications: Mapped[list["Publication"]] = relationship(back_populates="source")


class Publication(Base):
    """Un anuncio/disposición concreto publicado en un boletín."""

    __tablename__ = "publications"
    __table_args__ = (UniqueConstraint("source_id", "ext_id", name="uq_pub_source_ext"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    ext_id: Mapped[str] = mapped_column(String(64), index=True)   # p. ej. BOE-B-2024-12345
    pub_date: Mapped[date] = mapped_column(Date, index=True)
    section: Mapped[str] = mapped_column(String(255), default="")
    department: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(Text, default="")
    url_html: Mapped[str] = mapped_column(String(512), default="")
    url_pdf: Mapped[str] = mapped_column(String(512), default="")

    # Texto completo extraído (para búsqueda por nombre).
    full_text: Mapped[str] = mapped_column(Text, default="")
    # Texto normalizado para búsqueda laxa por nombre.
    normalized_text: Mapped[str] = mapped_column(Text, default="")
    # Identificadores fiscales válidos detectados en el texto (separados por espacio).
    identifiers: Mapped[str] = mapped_column(Text, default="")

    is_notification: Mapped[bool] = mapped_column(Boolean, default=False)  # TEU / notificaciones
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    source: Mapped[Source] = relationship(back_populates="publications")


class Match(Base):
    """Coincidencia entre una identidad vigilada y una publicación."""

    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("subject_id", "publication_id", name="uq_match_subject_pub"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"), index=True)
    match_type: Mapped[MatchType] = mapped_column(Enum(MatchType))
    matched_term: Mapped[str] = mapped_column(String(255), default="")
    score: Mapped[int] = mapped_column(Integer, default=100)  # 0-100 confianza

    notified: Mapped[bool] = mapped_column(Boolean, default=False)
    seen: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    subject: Mapped[Subject] = relationship(back_populates="matches")
    publication: Mapped[Publication] = relationship()


class Notification(Base):
    """Registro de aviso enviado al usuario (auditoría / no duplicar)."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(32), default="email")
    subject_line: Mapped[str] = mapped_column(String(512), default="")
    match_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="sent")  # sent / failed
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class IngestLog(Base):
    """Control de qué fechas/boletines se han ingerido (para backfill idempotente)."""

    __tablename__ = "ingest_log"
    __table_args__ = (UniqueConstraint("source_code", "pub_date", name="uq_ingest_source_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_code: Mapped[str] = mapped_column(String(32), index=True)
    pub_date: Mapped[date] = mapped_column(Date, index=True)
    items: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="ok")  # ok / empty / error
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
