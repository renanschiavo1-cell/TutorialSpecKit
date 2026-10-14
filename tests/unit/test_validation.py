"""Limites dos contratos de domínio, independentemente da interface."""

from dataclasses import replace

import pytest

from potatogene.domain.errors import ValidationError
from potatogene.domain.models import MarkerInput, SIZES, VarietyInput
from potatogene.domain.validation import (
    normalized_key, validate_id, validate_marker, validate_variety,
)

BASE = VarietyInput("Ágata", "Brasil", "Amarela", "Creme", "Pequeno")


@pytest.mark.parametrize("field,limit", [
    ("name", 100), ("origin", 100), ("skin_color", 50), ("flesh_color", 50),
])
@pytest.mark.parametrize("length", [1, "max"])
def test_text_limits(field, limit, length):
    text = "á" * (limit if length == "max" else length)
    assert getattr(validate_variety(replace(BASE, **{field: text})), field) == text


@pytest.mark.parametrize("field,limit", [
    ("name", 100), ("origin", 100), ("skin_color", 50), ("flesh_color", 50),
])
@pytest.mark.parametrize("invalid", ["", "   ", None, 3, True, [], "above"])
def test_invalid_fields(field, limit, invalid):
    value = "a" * (limit + 1) if invalid == "above" else invalid
    with pytest.raises(ValidationError) as error:
        validate_variety(replace(BASE, **{field: value}))
    assert field in error.value.fields


@pytest.mark.parametrize("control", ["\n", "\r", "\t", "\0", "\u200b", "\u2028", "\u2029"])
@pytest.mark.parametrize("field", ["name", "origin", "skin_color", "flesh_color"])
def test_reject_controls_including_external_control(field, control):
    for value in [f"a{control}b", f"{control}válido{control}"]:
        with pytest.raises(ValidationError):
            validate_variety(replace(BASE, **{field: value}))


@pytest.mark.parametrize("size", SIZES)
def test_valid_sizes(size):
    assert validate_variety(replace(BASE, size=size)).size == size


@pytest.mark.parametrize("size", [None, "", "pequeno", "Gigante", 1, True, []])
def test_invalid_sizes(size):
    with pytest.raises(ValidationError):
        validate_variety(replace(BASE, size=size))


@pytest.mark.parametrize("value", [True, False, None, 0, -1, "1", 1.5, []])
def test_invalid_ids(value):
    with pytest.raises(ValidationError):
        validate_id(value)


def test_valid_id_and_normalization():
    assert validate_id(1) == 1
    assert normalized_key(" Straße ") == "strasse"
    clean = validate_variety(replace(BASE, name="  D'Ágata - Demo  ", origin=" Desconhecida "))
    assert clean.name == "D'Ágata - Demo"
    assert clean.origin == "Desconhecida"
    assert normalized_key("Á  GATA") == "á  gata"
    assert normalized_key("Ágata") != normalized_key("Agata")


@pytest.mark.parametrize("field,limit", [("code", 50), ("value", 100)])
def test_marker_boundaries(field, limit):
    base = MarkerInput("MK-01", "A")
    for length in [1, limit]:
        value = "x" * length
        assert getattr(validate_marker(replace(base, **{field: value})), field) == value
    for value in ["", "  ", "x" * (limit + 1), None, 1, "A\nB", "\tA\t"]:
        with pytest.raises(ValidationError):
            validate_marker(replace(base, **{field: value}))


def test_multiple_errors_and_input_types():
    with pytest.raises(ValidationError) as error:
        validate_variety(VarietyInput("", "", "", "", None))
    assert len(error.value.fields) == 5
    with pytest.raises(ValidationError):
        validate_variety({"name": "Demo"})
    with pytest.raises(ValidationError):
        validate_marker(None)
