"""Manejo del navegador y del inicio de sesión en HabitatSoft."""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PWTimeout, sync_playwright

from .config import Credenciales

log = logging.getLogger("habitasoft")


class Sesion:
    """Abre un navegador Playwright e inicia sesión en el panel de gestión."""

    def __init__(self, config: dict, headful: bool = False,
                 capturas_dir: Path | None = None):
        self.config = config
        self.headful = headful
        self.capturas_dir = capturas_dir or Path("capturas")
        self.capturas_dir.mkdir(parents=True, exist_ok=True)
        self._pw = None
        self._browser = None
        self.page: Page | None = None

    def __enter__(self) -> "Sesion":
        self._pw = sync_playwright().start()
        # headless=False (headful) es necesario para resolver captcha manualmente.
        self._browser = self._pw.chromium.launch(headless=not self.headful)
        self.page = self._browser.new_context(locale="es-ES").new_page()
        return self

    def __exit__(self, *exc):
        try:
            if self._browser:
                self._browser.close()
        finally:
            if self._pw:
                self._pw.stop()

    def captura(self, nombre: str) -> Path:
        ruta = self.capturas_dir / f"{nombre}.png"
        if self.page:
            self.page.screenshot(path=str(ruta), full_page=True)
            log.info("Captura guardada: %s", ruta)
        return ruta

    def login(self, cred: Credenciales) -> None:
        cfg = self.config["login"]
        page = self.page
        assert page is not None

        log.info("Abriendo login: %s", cfg["url"])
        page.goto(cfg["url"], wait_until="domcontentloaded")

        page.fill(cfg["selector_usuario"], cred.usuario)
        page.fill(cfg["selector_password"], cred.password)

        if cred.inmobiliaria and cfg.get("selector_inmobiliaria"):
            sel = cfg["selector_inmobiliaria"]
            if page.locator(sel).count():
                try:
                    page.fill(sel, cred.inmobiliaria)
                except Exception:
                    log.debug("No se pudo rellenar el campo de inmobiliaria (%s)", sel)

        # ¿Captcha visible? No se puede resolver de forma automática.
        sel_captcha = cfg.get("selector_captcha")
        if sel_captcha and page.locator(sel_captcha).is_visible():
            if not self.headful:
                self.captura("captcha")
                raise RuntimeError(
                    "Apareció un captcha en el login. Vuelve a ejecutar con --headful "
                    "para resolverlo a mano."
                )
            log.warning("Captcha detectado: resuélvelo en la ventana del navegador. "
                        "Tienes 120 s...")
            page.wait_for_selector(sel_captcha, state="hidden", timeout=120_000)

        page.click(cfg["selector_boton"])

        sel_ok = cfg.get("selector_login_ok")
        try:
            if sel_ok:
                page.wait_for_selector(sel_ok, timeout=20_000)
            else:
                page.wait_for_load_state("networkidle", timeout=20_000)
        except PWTimeout:
            self.captura("login_fallido")
            raise RuntimeError(
                "No se confirmó el inicio de sesión. Revisa credenciales o el "
                "selector 'login_ok' (captura: login_fallido.png)."
            )
        log.info("Sesión iniciada correctamente.")
