"""Fixtures sem acesso ao catálogo real do usuário."""

from dataclasses import asdict

import pytest

from potatogene.data.database import Database
from potatogene.domain.errors import DuplicateError, NotFoundError
from potatogene.domain.models import DEMONSTRATIVE_SOURCE, Variety, VarietyInput


@pytest.fixture(autouse=True)
def isolated_path(tmp_path, monkeypatch):
    path = tmp_path / "catalog.db"
    monkeypatch.setenv("POTATOGENE_DB_PATH", str(path))
    return path


@pytest.fixture
def database(isolated_path):
    db = Database(isolated_path)
    db.initialize()
    return db


@pytest.fixture
def variety_input():
    return VarietyInput("Ágata Demo", "Brasil", "Amarela", "Creme", "Pequeno")


@pytest.fixture
def seed_marker():
    """Inserção de fixture para cascade; não implementa gerenciamento de US3."""
    def insert(db, variety_id, code="MK-01", value="A"):
        with db.session(write=True) as connection:
            cursor = connection.execute(
                "INSERT INTO markers(variety_id, code, code_key, value, source) VALUES (?, ?, ?, ?, ?)",
                (variety_id, code, code.strip().casefold(), value, DEMONSTRATIVE_SOURCE),
            )
            return cursor.lastrowid
    return insert


class MemoryVarietyRepository:
    """Substituto de dados que demonstra negócio testável sem SQLite/Streamlit."""

    def __init__(self):
        self.records = {}
        self.next_id = 1

    def list(self):
        return sorted(self.records.values(), key=lambda record: (record.name_key, record.id))

    def get(self, record_id):
        if record_id not in self.records:
            raise NotFoundError("Variedade não encontrada. Selecione novamente.")
        return self.records[record_id]

    def exists_name(self, key, exclude_id=None):
        return any(record.name_key == key and record.id != exclude_id for record in self.records.values())

    def create(self, data, key):
        if self.exists_name(key):
            raise DuplicateError("Nome já cadastrado.")
        record = Variety(id=self.next_id, name_key=key, **asdict(data))
        self.next_id += 1
        self.records[record.id] = record
        return record

    def update(self, record_id, data, key):
        self.get(record_id)
        if self.exists_name(key, record_id):
            raise DuplicateError("Nome já cadastrado.")
        record = Variety(id=record_id, name_key=key, **asdict(data))
        self.records[record_id] = record
        return record

    def delete(self, record_id):
        self.get(record_id)
        del self.records[record_id]


@pytest.fixture
def memory_repository():
    return MemoryVarietyRepository()
