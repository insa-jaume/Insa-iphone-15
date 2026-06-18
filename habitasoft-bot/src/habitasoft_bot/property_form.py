"""Motor genérico que rellena el formulario de alta de propiedad."""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import Page

log = logging.getLogger("habitasoft")


def _valor_para(campo: dict, valor) -> str:
    """Aplica mapa_valores (si existe) y normaliza a string."""
    mapa = campo.get("mapa_valores")
    if mapa and valor in mapa:
        return str(mapa[valor])
    return str(valor)


def rellenar_formulario(page: Page, cfg_alta: dict, propiedad: dict) -> None:
    """Rellena cada campo del formulario según el mapeo de config."""
    for campo in cfg_alta.get("campos", []):
        clave = campo["dato"]
        if clave not in propiedad or propiedad[clave] in (None, ""):
            log.debug("Sin dato para '%s', se omite.", clave)
            continue

        selector = campo["selector"]
        tipo = campo.get("tipo", "text")
        valor = _valor_para(campo, propiedad[clave])

        loc = page.locator(selector)
        if not loc.count():
            log.warning("Selector no encontrado para '%s': %s (se omite)", clave, selector)
            continue

        if tipo in ("text", "number", "textarea"):
            loc.fill(valor)
        elif tipo == "select":
            try:
                loc.select_option(value=valor)
            except Exception:
                loc.select_option(label=valor)
        elif tipo == "checkbox":
            if str(valor).lower() in ("1", "true", "si", "sí", "yes"):
                loc.check()
            else:
                loc.uncheck()
        elif tipo == "radio":
            page.locator(f"{selector}[value='{valor}']").check()
        else:
            log.warning("Tipo de campo desconocido '%s' en '%s'", tipo, clave)
            continue
        log.info("Campo '%s' -> %s", clave, valor)


def subir_fotos(page: Page, cfg_alta: dict, propiedad: dict, base_dir: Path) -> None:
    fotos = propiedad.get("fotos") or []
    if not fotos:
        log.info("La propiedad no tiene fotos.")
        return
    selector = cfg_alta.get("fotos", {}).get("selector_input_file")
    if not selector:
        log.warning("No hay 'selector_input_file' configurado; se omiten fotos.")
        return

    rutas = []
    for f in fotos:
        p = Path(f)
        if not p.is_absolute():
            p = base_dir / p
        if not p.exists():
            log.warning("Foto no encontrada: %s (se omite)", p)
            continue
        rutas.append(str(p))

    if not rutas:
        return
    page.locator(selector).set_input_files(rutas)
    log.info("Subidas %d fotos.", len(rutas))


def guardar(page: Page, cfg_alta: dict) -> bool:
    """Pulsa guardar y comprueba la confirmación. Devuelve True si parece OK."""
    g = cfg_alta.get("guardar", {})
    boton = g.get("selector_boton")
    if not boton:
        log.warning("No hay 'guardar.selector_boton' configurado.")
        return False
    page.click(boton)

    confirm = g.get("selector_confirmacion")
    if confirm:
        try:
            page.wait_for_selector(confirm, timeout=20_000)
            log.info("Propiedad guardada (confirmación detectada).")
            return True
        except Exception:
            log.error("No se detectó la confirmación de guardado.")
            return False
    page.wait_for_load_state("networkidle", timeout=20_000)
    return True
