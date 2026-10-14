"""Entradas e registros; identidade e origem não são inputs editáveis."""

from dataclasses import dataclass

SIZES = ("Pequeno", "Médio", "Grande")
DEMONSTRATIVE_SOURCE = "Demonstrativo — exemplo educacional"


@dataclass(frozen=True)
class VarietyInput:
    """Os cinco campos informados pelo usuário."""

    name: str
    origin: str
    skin_color: str
    flesh_color: str
    size: str


@dataclass(frozen=True)
class Variety:
    """Variedade persistida com ID estável e nome normalizado único."""

    id: int
    name: str
    name_key: str
    origin: str
    skin_color: str
    flesh_color: str
    size: str


@dataclass(frozen=True)
class MarkerInput:
    """Entrada demonstrativa prevista no modelo, sem operações de US3."""

    code: str
    value: str


@dataclass(frozen=True)
class Marker:
    """Registro associado usado na integridade da fundação."""

    id: int
    variety_id: int
    code: str
    code_key: str
    value: str
    source: str
