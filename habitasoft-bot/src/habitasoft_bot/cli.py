"""Interfaz de línea de comandos del bot de HabitatSoft.

Comandos:
  login      Comprueba que las credenciales funcionan.
  calibrar   Inicia sesión y vuelca los campos del formulario de alta.
  crear      Da de alta una propiedad a partir de una ficha YAML.

La opción --dry-run rellena el formulario pero NO pulsa guardar.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import calibrate, property_form
from .config import cargar_config, cargar_credenciales, cargar_propiedad
from .session import Sesion


def _logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="habitasoft-bot", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=Path("config.yaml"),
                   help="Ruta al config.yaml (por defecto: ./config.yaml)")
    p.add_argument("--env", type=Path, default=None, help="Ruta a un archivo .env")
    p.add_argument("--headful", action="store_true",
                   help="Muestra el navegador (necesario para captchas)")
    p.add_argument("-v", "--verbose", action="store_true")

    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("login", help="Verifica el inicio de sesión")
    sub.add_parser("calibrar", help="Vuelca los campos del formulario de alta")

    c = sub.add_parser("crear", help="Crea una propiedad desde una ficha YAML")
    c.add_argument("ficha", type=Path, help="YAML de la propiedad")
    c.add_argument("--dry-run", action="store_true",
                   help="Rellena el formulario pero NO guarda")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    _logging(args.verbose)

    config = cargar_config(args.config)
    cred = cargar_credenciales(args.env)

    with Sesion(config, headful=args.headful) as s:
        s.login(cred)

        if args.comando == "login":
            print("OK: inicio de sesión correcto.")
            return 0

        if args.comando == "calibrar":
            calibrate.calibrar(s.page, config["alta_propiedad"], Path("calibracion"))
            print("Calibración terminada. Revisa la carpeta ./calibracion")
            return 0

        if args.comando == "crear":
            propiedad = cargar_propiedad(args.ficha)
            cfg_alta = config["alta_propiedad"]
            base_dir = args.ficha.resolve().parent

            url = cfg_alta.get("url")
            if url:
                s.page.goto(url, wait_until="domcontentloaded")
            boton_nuevo = cfg_alta.get("selector_boton_nuevo")
            if boton_nuevo and s.page.locator(boton_nuevo).count():
                s.page.click(boton_nuevo)
                s.page.wait_for_load_state("networkidle", timeout=20_000)

            property_form.rellenar_formulario(s.page, cfg_alta, propiedad)
            property_form.subir_fotos(s.page, cfg_alta, propiedad, base_dir)

            if args.dry_run:
                s.captura("dry_run")
                print("DRY-RUN: formulario relleno pero NO guardado. "
                      "Captura en capturas/dry_run.png")
                return 0

            ok = property_form.guardar(s.page, cfg_alta)
            s.captura("resultado")
            if ok:
                print("OK: propiedad creada.")
                return 0
            print("ERROR: no se confirmó el guardado. Revisa capturas/resultado.png")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
