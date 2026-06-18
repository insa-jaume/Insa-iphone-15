"""Carga de configuración (YAML) y credenciales (variables de entorno / .env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass
class Credenciales:
    usuario: str
    password: str
    inmobiliaria: str | None = None


def cargar_credenciales(env_path: Path | None = None) -> Credenciales:
    """Lee las credenciales SOLO de variables de entorno / .env.

    Nunca se guardan en el repositorio ni en la configuración.
    """
    if env_path and env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # busca un .env en el cwd / padres

    usuario = os.getenv("HABITASOFT_USER")
    password = os.getenv("HABITASOFT_PASSWORD")
    inmobiliaria = os.getenv("HABITASOFT_INMOBILIARIA") or None

    faltan = [n for n, v in (("HABITASOFT_USER", usuario),
                             ("HABITASOFT_PASSWORD", password)) if not v]
    if faltan:
        raise SystemExit(
            "Faltan credenciales en el entorno: " + ", ".join(faltan) +
            "\nCopia .env.example a .env y rellénalo, o expórtalas como variables de entorno."
        )
    return Credenciales(usuario=usuario, password=password, inmobiliaria=inmobiliaria)


def cargar_config(ruta: Path) -> dict:
    if not ruta.exists():
        raise SystemExit(
            f"No existe el archivo de configuración: {ruta}\n"
            "Copia config.example.yaml a config.yaml y ajústalo."
        )
    with ruta.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cargar_propiedad(ruta: Path) -> dict:
    if not ruta.exists():
        raise SystemExit(f"No existe la ficha de propiedad: {ruta}")
    with ruta.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
