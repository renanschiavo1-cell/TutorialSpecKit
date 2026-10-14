"""Validação aplicada no negócio antes de qualquer persistência."""

import unicodedata
from dataclasses import fields

from potatogene.domain.errors import ValidationError
from potatogene.domain.models import MarkerInput, SIZES, VarietyInput

FIELD_RULES = {
    "name": ("Nome", 100),
    "origin": ("Origem", 100),
    "skin_color": ("Cor da casca", 50),
    "flesh_color": ("Cor da polpa", 50),
    "code": ("Código", 50),
    "value": ("Valor", 100),
}


def normalized_key(text: str) -> str:
    """Equivalência Unicode; mantém acentos e espaços internos."""
    return text.strip().casefold()


def validate_id(value: int) -> int:
    """Aceite somente inteiro positivo, excluindo bool."""
    if type(value) is not int or value <= 0:
        raise ValidationError({"id": "Seleção inválida. Escolha um registro existente."})
    return value


def _text(value: str, field: str) -> str:
    label, limit = FIELD_RULES[field]
    if not isinstance(value, str):
        raise ValidationError({field: f"{label}: informe um texto."})
    # Verificar antes de strip evita aceitar uma quebra/controle removida nas bordas.
    if any(unicodedata.category(char) in {"Cc", "Cf", "Zl", "Zp"} for char in value):
        raise ValidationError({field: f"{label}: use uma linha, sem caracteres de controle."})
    clean = value.strip()
    if not 1 <= len(clean) <= limit:
        raise ValidationError({field: f"{label}: informe de 1 a {limit} caracteres."})
    return clean


def _validate(input_value, expected_type):
    if not isinstance(input_value, expected_type):
        raise ValidationError({"input": "Dados de entrada inválidos."})
    errors = {}
    clean = {}
    for field in fields(expected_type):
        value = getattr(input_value, field.name)
        try:
            if field.name == "size":
                if not isinstance(value, str) or value not in SIZES:
                    raise ValidationError({"size": "Tamanho: selecione Pequeno, Médio ou Grande."})
                clean[field.name] = value
            else:
                clean[field.name] = _text(value, field.name)
        except ValidationError as error:
            errors.update(error.fields)
    if errors:
        raise ValidationError(errors)
    return expected_type(**clean)


def validate_variety(value: VarietyInput) -> VarietyInput:
    """Valide os cinco campos e devolva uma entrada limpa, sem mutar o original."""
    return _validate(value, VarietyInput)


def validate_marker(value: MarkerInput) -> MarkerInput:
    """Valide código/valor demonstrativos, sem validar ciência nem origem editável."""
    return _validate(value, MarkerInput)
