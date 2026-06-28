"""Normalización y validación de identificadores y nombres españoles.

El núcleo del servicio es poder localizar de forma fiable a una persona o
empresa dentro del texto de los boletines. Para ello normalizamos:

* Identificadores fiscales: DNI, NIE, NIF y CIF.
* Nombres y razones sociales (sin tildes, mayúsculas, espacios colapsados).

La coincidencia por identificador es de altísima precisión (casi sin falsos
positivos). La coincidencia por nombre es de apoyo y siempre se marca como
"revisión recomendada".
"""
from __future__ import annotations

import re
import unicodedata

# --- Tablas oficiales de control ---------------------------------------------

_DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
# Letras de control para CIF (sociedades): posiciones 0-9 -> JABCDEFGHI
_CIF_CONTROL = "JABCDEFGHI"
_NIE_PREFIX = {"X": "0", "Y": "1", "Z": "2"}


def strip_accents(text: str) -> str:
    """Elimina tildes/diacríticos manteniendo la ñ como n (para búsqueda laxa)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name(name: str) -> str:
    """Normaliza un nombre o razón social para comparación.

    "José Mª  García-López, S.L." -> "JOSE MA GARCIA LOPEZ SL"
    """
    if not name:
        return ""
    text = strip_accents(name).upper()
    # Sustituye cualquier cosa que no sea alfanumérico por espacio.
    text = re.sub(r"[^A-Z0-9Ñ ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_identifier(value: str) -> str:
    """Normaliza un identificador fiscal: mayúsculas, sin espacios ni guiones."""
    if not value:
        return ""
    return re.sub(r"[^A-Z0-9]", "", value.upper())


# --- Validación ---------------------------------------------------------------

_DNI_RE = re.compile(r"^\d{8}[A-Z]$")
_NIE_RE = re.compile(r"^[XYZ]\d{7}[A-Z]$")
_CIF_RE = re.compile(r"^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$")


def _dni_letter(number: int) -> str:
    return _DNI_LETTERS[number % 23]


def validate_dni(value: str) -> bool:
    v = normalize_identifier(value)
    if not _DNI_RE.match(v):
        return False
    return _dni_letter(int(v[:8])) == v[8]


def validate_nie(value: str) -> bool:
    v = normalize_identifier(value)
    if not _NIE_RE.match(v):
        return False
    number = int(_NIE_PREFIX[v[0]] + v[1:8])
    return _dni_letter(number) == v[8]


def validate_cif(value: str) -> bool:
    v = normalize_identifier(value)
    if not _CIF_RE.match(v):
        return False
    digits = v[1:8]
    suma_par = sum(int(d) for d in digits[1::2])
    suma_impar = 0
    for d in digits[0::2]:
        doble = int(d) * 2
        suma_impar += doble // 10 + doble % 10
    total = suma_par + suma_impar
    control_digit = (10 - (total % 10)) % 10
    control_char = v[8]
    # Según la primera letra, el control puede ser número o letra.
    if v[0] in "PQRSNW":  # control siempre letra
        return control_char == _CIF_CONTROL[control_digit]
    if v[0] in "ABEH":  # control siempre número
        return control_char == str(control_digit)
    # Resto: admite ambos
    return control_char == str(control_digit) or control_char == _CIF_CONTROL[control_digit]


def classify_identifier(value: str) -> str | None:
    """Devuelve 'DNI', 'NIE', 'CIF' o None si no es un identificador válido."""
    v = normalize_identifier(value)
    if validate_dni(v):
        return "DNI"
    if validate_nie(v):
        return "NIE"
    if validate_cif(v):
        return "CIF"
    return None


def is_valid_identifier(value: str) -> bool:
    return classify_identifier(value) is not None


# --- Extracción de identificadores de texto libre (boletines) -----------------

# Captura posibles DNI/NIE/CIF en texto, con o sin separadores.
# - DNI: 8 dígitos + letra de control (cualquier letra del cuadro oficial).
# - NIE: X/Y/Z + 7 dígitos + letra.
# - CIF: letra inicial + 7 dígitos + dígito/letra de control.
# La letra inicial opcional cubre el CIF; la validación posterior descarta el ruido.
_ID_CANDIDATE_RE = re.compile(
    r"\b([A-Za-z]?\d{7,8}[\-\.\s]?[0-9A-Za-z])\b",
    re.IGNORECASE,
)


def extract_identifiers(text: str) -> set[str]:
    """Extrae identificadores fiscales *válidos* presentes en un texto."""
    found: set[str] = set()
    for raw in _ID_CANDIDATE_RE.findall(text or ""):
        candidate = normalize_identifier(raw)
        if is_valid_identifier(candidate):
            found.add(candidate)
    return found
