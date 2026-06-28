"""Tests de normalización y validación de identificadores y nombres."""
from app.normalize import (
    classify_identifier,
    extract_identifiers,
    normalize_identifier,
    normalize_name,
    validate_cif,
    validate_dni,
    validate_nie,
)


def test_dni_valido():
    assert validate_dni("12345678Z")
    assert validate_dni("12345678-Z")
    assert not validate_dni("12345678A")  # letra incorrecta
    assert not validate_dni("1234567Z")   # longitud


def test_nie_valido():
    assert validate_nie("X1234567L")
    assert not validate_nie("X1234567A")


def test_cif_valido():
    # CIF reales conocidos (control correcto).
    assert validate_cif("A28015865")  # Telefónica
    assert not validate_cif("A28015860")


def test_clasificacion():
    assert classify_identifier("12345678Z") == "DNI"
    assert classify_identifier("X1234567L") == "NIE"
    assert classify_identifier("A28015865") == "CIF"
    assert classify_identifier("HOLA") is None


def test_normalizacion_nombre():
    assert normalize_name("José Mª  García-López, S.L.") == "JOSE MA GARCIA LOPEZ S L"
    # La ñ se normaliza a n para una comparación laxa (consistente texto/consulta).
    assert normalize_name("  Núñez   ") == "NUNEZ"


def test_normalizacion_identificador():
    assert normalize_identifier("12.345.678-z") == "12345678Z"


def test_extraccion_desde_texto():
    texto = (
        "Se notifica a D. Juan con DNI 12345678Z y a la mercantil "
        "EJEMPLO SL (A28015865). Otro número 99999999 no es válido."
    )
    ids = extract_identifiers(texto)
    assert "12345678Z" in ids
    assert "A28015865" in ids
