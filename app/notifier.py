"""Envío de avisos por email cuando aparecen nuevas coincidencias."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Match, Notification, Publication, Source, Subject, User

log = logging.getLogger("notifier")


def _send_email(to: str, subject: str, body_text: str, body_html: str) -> None:
    if not settings.email_enabled:
        log.warning("SMTP no configurado; email a %s NO enviado", to)
        raise RuntimeError("SMTP no configurado")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)


def _render(user: User, rows: list[tuple[Match, Publication, Source, Subject]]) -> tuple[str, str]:
    lines = [f"Hola {user.full_name or user.email},", "",
             f"Hemos detectado {len(rows)} nueva(s) publicación(es) que coinciden "
             "con los datos que vigilas:", ""]
    html = [f"<p>Hola {user.full_name or user.email},</p>",
            f"<p>Hemos detectado <b>{len(rows)}</b> nueva(s) publicación(es) "
            "que coinciden con los datos que vigilas:</p><ul>"]
    for match, pub, source, subject in rows:
        tipo = "identificador" if match.match_type.value == "identifier" else "nombre (revisar)"
        url = pub.url_html or pub.url_pdf or ""
        lines.append(f"- [{source.code}] {pub.pub_date} · {subject.display_name} ({tipo})")
        lines.append(f"  {pub.title[:160]}")
        if url:
            lines.append(f"  {url}")
        lines.append("")
        html.append(
            f"<li><b>[{source.code}]</b> {pub.pub_date} · {subject.display_name} "
            f"<i>({tipo})</i><br>{pub.title[:200]}<br>"
            + (f'<a href="{url}">Ver publicación oficial</a>' if url else "")
            + "</li>"
        )
    html.append("</ul>")
    html.append(f'<p style="color:#888;font-size:12px">{settings.site_name}. '
                "Este aviso es informativo; verifica siempre en la fuente oficial. "
                "Puedes gestionar o cancelar tu suscripción desde tu panel.</p>")
    lines.append(f"-- {settings.site_name}")
    return "\n".join(lines), "\n".join(html)


def notify_pending(db: Session) -> int:
    """Envía un email por usuario agrupando sus coincidencias sin notificar.

    Devuelve el número de usuarios notificados.
    """
    pending = db.scalars(
        select(Match).where(Match.notified.is_(False)).order_by(Match.subject_id)
    ).all()
    if not pending:
        return 0

    # Agrupar por usuario.
    by_user: dict[int, list[tuple[Match, Publication, Source, Subject]]] = {}
    for match in pending:
        subject = db.get(Subject, match.subject_id)
        if subject is None:
            continue
        pub = db.get(Publication, match.publication_id)
        source = db.get(Source, pub.source_id) if pub else None
        by_user.setdefault(subject.user_id, []).append((match, pub, source, subject))

    notified_users = 0
    for user_id, rows in by_user.items():
        user = db.get(User, user_id)
        if user is None:
            continue
        # Solo notificamos a usuarios con suscripción activa.
        if not user.has_active_subscription:
            continue

        subject_line = f"[{settings.site_name}] {len(rows)} nueva(s) coincidencia(s) en boletines"
        text, html = _render(user, rows)
        status, error = "sent", ""
        try:
            _send_email(user.email, subject_line, text, html)
            notified_users += 1
            for match, *_ in rows:
                match.notified = True
        except Exception as exc:  # noqa: BLE001
            status, error = "failed", str(exc)[:500]
            log.exception("Fallo enviando aviso a %s", user.email)

        db.add(Notification(
            user_id=user.id, channel="email", subject_line=subject_line,
            match_count=len(rows), status=status, error=error,
        ))
        db.commit()

    return notified_users
