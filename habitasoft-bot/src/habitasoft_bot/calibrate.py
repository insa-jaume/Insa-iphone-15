"""Calibración: vuelca los campos reales del formulario de alta para mapearlos."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from playwright.sync_api import Page

log = logging.getLogger("habitasoft")

# JS que extrae todos los controles de formulario visibles de la página.
_JS_EXTRAER = r"""
() => {
  const out = [];
  const els = document.querySelectorAll('input, select, textarea');
  els.forEach(el => {
    const tipo = (el.tagName === 'SELECT') ? 'select'
               : (el.tagName === 'TEXTAREA') ? 'textarea'
               : (el.type || 'text');
    if (['hidden'].includes(tipo)) return;
    let label = '';
    if (el.id) {
      const l = document.querySelector(`label[for="${el.id}"]`);
      if (l) label = l.innerText.trim();
    }
    if (!label && el.placeholder) label = el.placeholder;
    if (!label && el.name) label = el.name;
    const item = {
      etiqueta: label,
      tipo,
      id: el.id || '',
      name: el.name || '',
      selector: el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : ''),
    };
    if (el.tagName === 'SELECT') {
      item.opciones = Array.from(el.options)
        .slice(0, 50)
        .map(o => ({ value: o.value, label: o.text.trim() }));
    }
    out.push(item);
  });
  return out;
}
"""


def calibrar(page: Page, cfg_alta: dict, salida_dir: Path) -> Path:
    """Navega al formulario de alta y vuelca sus campos a un archivo JSON."""
    salida_dir.mkdir(parents=True, exist_ok=True)

    url = cfg_alta.get("url")
    if url:
        log.info("Navegando al formulario de alta: %s", url)
        page.goto(url, wait_until="domcontentloaded")

    boton_nuevo = cfg_alta.get("selector_boton_nuevo")
    if boton_nuevo:
        if page.locator(boton_nuevo).count():
            page.click(boton_nuevo)
            page.wait_for_load_state("networkidle", timeout=20_000)

    page.wait_for_load_state("networkidle", timeout=20_000)

    campos = page.evaluate(_JS_EXTRAER)

    json_path = salida_dir / "calibracion.json"
    json_path.write_text(json.dumps(campos, indent=2, ensure_ascii=False), encoding="utf-8")

    html_path = salida_dir / "formulario.html"
    html_path.write_text(page.content(), encoding="utf-8")

    png_path = salida_dir / "formulario.png"
    page.screenshot(path=str(png_path), full_page=True)

    log.info("Encontrados %d campos. Revisa: %s", len(campos), json_path)
    log.info("HTML completo: %s | Captura: %s", html_path, png_path)
    return json_path
