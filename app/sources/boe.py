"""Adaptador para el BOE y el BORME mediante la API oficial de datos abiertos.

API: https://www.boe.es/datosabiertos/api/boe/sumario/{AAAAMMDD}
     https://www.boe.es/datosabiertos/api/borme/sumario/{AAAAMMDD}
Respuesta: JSON (Accept: application/json) o XML.

La reutilización se hace conforme a las condiciones de reutilización publicadas
por la Agencia Estatal BOE, identificándonos con un User-Agent propio y con un
ritmo de peticiones moderado.
"""
from __future__ import annotations

import re
from datetime import date

from app.sources.base import BulletinSource, RawItem, html_to_text

_BOE_HOST = "https://www.boe.es"


def _as_list(value) -> list:
    """El JSON del BOE usa indistintamente objeto único o lista; lo normalizamos."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _url(path) -> str:
    """Resuelve una URL del BOE, que en el JSON puede ser str o {'texto': ...}."""
    if isinstance(path, dict):
        path = path.get("texto") or path.get("url") or ""
    if not path:
        return ""
    if path.startswith("http"):
        return path
    return _BOE_HOST + path


_TEXTO_RE = re.compile(r"<texto>(.*?)</texto>", re.IGNORECASE | re.DOTALL)


class _BoeFamilySource(BulletinSource):
    """Lógica compartida BOE/BORME (misma estructura de sumario)."""

    api_path: str = ""  # "boe" o "borme"

    def fetch_summary_items(self, day: date) -> list[RawItem]:
        url = f"{_BOE_HOST}/datosabiertos/api/{self.api_path}/sumario/{day:%Y%m%d}"
        resp = self._get(url, accept="application/json")
        if resp.status_code == 404:
            return []  # no hubo boletín ese día (festivo/domingo)
        resp.raise_for_status()
        payload = resp.json()
        return list(self._walk(payload, day))

    def _walk(self, payload: dict, day: date):
        sumario = (payload or {}).get("data", {}).get("sumario", {})
        for diario in _as_list(sumario.get("diario")):
            for seccion in _as_list(diario.get("seccion")):
                sec_name = seccion.get("nombre", "")
                sec_code = str(seccion.get("codigo", ""))
                is_notif_section = sec_code == "5" or "anuncios" in sec_name.lower()
                for depto in _as_list(seccion.get("departamento")):
                    dep_name = depto.get("nombre", "")
                    # Los items pueden colgar de "epigrafe" o directamente del departamento.
                    epigrafes = _as_list(depto.get("epigrafe"))
                    if epigrafes:
                        for epi in epigrafes:
                            epi_name = epi.get("nombre", "")
                            for item in _as_list(epi.get("item")):
                                yield self._make_item(
                                    item, day, sec_name, dep_name, epi_name, is_notif_section
                                )
                    else:
                        for item in _as_list(depto.get("item")):
                            yield self._make_item(
                                item, day, sec_name, dep_name, "", is_notif_section
                            )

    def _make_item(self, item, day, section, department, epigrafe, notif_section) -> RawItem:
        title = item.get("titulo", "")
        blob = f"{epigrafe} {title}".lower()
        is_notification = notif_section or "notificaci" in blob or "edicto" in blob
        return RawItem(
            ext_id=item.get("identificador", ""),
            title=title,
            pub_date=day,
            section=section,
            department=department,
            epigrafe=epigrafe,
            url_html=_url(item.get("url_html")),
            url_pdf=_url(item.get("url_pdf")),
            url_xml=_url(item.get("url_xml")),
            is_notification=is_notification,
        )

    def fetch_item_text(self, item: RawItem) -> str:
        # Preferimos el XML estructurado; si no, el HTML del diario.
        url = item.url_xml or item.url_html
        if not url:
            return item.title
        resp = self._get(url, accept="application/xml")
        if resp.status_code != 200:
            return item.title
        body = resp.text
        m = _TEXTO_RE.search(body)
        chunk = m.group(1) if m else body
        text = html_to_text(chunk)
        # Anteponemos el título por si el cuerpo no lo repite.
        return f"{item.title}\n{text}".strip()


class BoeSource(_BoeFamilySource):
    code = "BOE"
    name = "Boletín Oficial del Estado"
    api_path = "boe"


class BormeSource(_BoeFamilySource):
    code = "BORME"
    name = "Boletín Oficial del Registro Mercantil"
    api_path = "borme"
