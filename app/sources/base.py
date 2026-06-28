"""Interfaz común a todos los adaptadores de boletines.

Añadir un boletín nuevo (autonómico o provincial) consiste en crear una
subclase de :class:`BulletinSource` que sepa:

1. listar los anuncios/disposiciones de un día concreto (``fetch_summary_items``),
2. obtener el texto completo de cada uno (``fetch_item_text``).

El resto del sistema (deduplicado, extracción de identificadores, matching,
notificación) es agnóstico a la fuente.
"""
from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date

import httpx

from app.config import settings

_USER_AGENT = (
    f"{settings.site_name}/1.0 (servicio de alertas a titulares; "
    f"contacto: {settings.provider_email})"
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def html_to_text(html: str) -> str:
    """Convierte HTML/XML simple a texto plano legible."""
    if not html:
        return ""
    text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n", text, flags=re.IGNORECASE)
    text = _TAG_RE.sub(" ", text)
    text = (
        text.replace("&aacute;", "á").replace("&eacute;", "é")
        .replace("&iacute;", "í").replace("&oacute;", "ó").replace("&uacute;", "ú")
        .replace("&ntilde;", "ñ").replace("&Ntilde;", "Ñ")
        .replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
        .replace("&lt;", "<").replace("&gt;", ">")
    )
    return _WS_RE.sub(" ", text).strip()


@dataclass
class RawItem:
    """Un anuncio/disposición tal y como aparece en el sumario de un boletín."""

    ext_id: str
    title: str
    pub_date: date
    section: str = ""
    department: str = ""
    epigrafe: str = ""
    url_html: str = ""
    url_pdf: str = ""
    url_xml: str = ""
    is_notification: bool = False
    extra: dict = field(default_factory=dict)


class BulletinSource(ABC):
    """Clase base para un boletín oficial."""

    code: str = ""
    name: str = ""

    def __init__(self) -> None:
        self._client = httpx.Client(
            headers={"User-Agent": _USER_AGENT},
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    # -- HTTP con reintentos y cortesía ---------------------------------------

    def _get(self, url: str, *, accept: str | None = None) -> httpx.Response:
        headers = {"Accept": accept} if accept else {}
        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                resp = self._client.get(url, headers=headers)
                time.sleep(settings.ingest_request_delay)
                return resp
            except httpx.HTTPError as exc:  # red caída / timeout
                last_exc = exc
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Fallo de red tras reintentos: {url}") from last_exc

    # -- Interfaz a implementar -----------------------------------------------

    @abstractmethod
    def fetch_summary_items(self, day: date) -> list[RawItem]:
        """Devuelve los anuncios publicados ese día (lista vacía si no hubo)."""

    @abstractmethod
    def fetch_item_text(self, item: RawItem) -> str:
        """Descarga y devuelve el texto completo de un anuncio."""

    def close(self) -> None:
        self._client.close()
