"""Caminho do catálogo independente do diretório corrente."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def database_path() -> Path:
    """Retorne o caminho padrão ou POTATOGENE_DB_PATH, sem fallback em erro."""
    override = os.environ.get("POTATOGENE_DB_PATH")
    path = Path(override) if override else Path("data/potatogene.db")
    return path if path.is_absolute() else PROJECT_ROOT / path
