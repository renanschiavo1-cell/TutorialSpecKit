"""Falhas durante operações reais: rollback e fechamento, sem dados parciais."""

import sqlite3
from dataclasses import replace

import pytest

from potatogene.data.database import Database
from potatogene.data.repositories import VarietyRepository
from potatogene.domain.errors import StorageError
from potatogene.services.varieties import VarietyService


@pytest.mark.parametrize("operation", ["create", "update", "delete"])
def test_commit_failure_preserves_every_record(database, variety_input, seed_marker, monkeypatch, operation):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(variety_input)
    seed_marker(database, saved.id)
    closed_connections = []
    original_connect = database._connect

    def capture(*args, **kwargs):
        connection = original_connect(*args, **kwargs)
        closed_connections.append(connection)
        return connection

    monkeypatch.setattr(database, "_connect", capture)
    def fail_commit(connection):
        raise sqlite3.OperationalError("injected commit failure")

    # Apenas escrita falha; pré-consultas precisam completar suas leituras normalmente.
    original_commit = database._commit
    def fail_write_commit(connection):
        if connection.total_changes:
            fail_commit(connection)
        original_commit(connection)

    with monkeypatch.context() as scoped:
        scoped.setattr(database, "_commit", fail_write_commit)
        with pytest.raises(StorageError):
            if operation == "create":
                service.create(replace(variety_input, name="Nova"))
            elif operation == "update":
                service.update(saved.id, replace(variety_input, origin="Outra"))
            else:
                service.delete(saved.id)
    assert service.list() == [saved]
    with database.session() as connection:
        assert connection.execute("SELECT COUNT(*) FROM markers").fetchone()[0] == 1
    for connection in closed_connections:
        with pytest.raises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")


def test_read_failure_never_returns_empty_catalog(database, variety_input, monkeypatch):
    service = VarietyService(VarietyRepository(database))
    service.create(variety_input)
    def fail_connect(*args, **kwargs):
        raise sqlite3.OperationalError("injected read failure")
    monkeypatch.setattr(database, "_connect", fail_connect)
    with pytest.raises(StorageError):
        service.list()


def test_partial_delete_rollback(database, variety_input, seed_marker):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(variety_input)
    seed_marker(database, saved.id)
    with pytest.raises(StorageError):
        with database.session(write=True) as connection:
            connection.execute("DELETE FROM varieties WHERE id=?", (saved.id,))
            raise sqlite3.OperationalError("failure after cascade")
    assert service.get(saved.id) == saved
    with database.session() as connection:
        assert connection.execute("SELECT COUNT(*) FROM markers").fetchone()[0] == 1


def test_locked_database_preserves_data(database, variety_input):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(variety_input)
    locked = sqlite3.connect(database.path, isolation_level=None)
    try:
        locked.execute("BEGIN IMMEDIATE")
        impatient = VarietyService(VarietyRepository(Database(database.path, timeout=0.01)))
        with pytest.raises(StorageError):
            impatient.update(saved.id, replace(variety_input, origin="Outra"))
    finally:
        locked.rollback()
        locked.close()
    assert service.get(saved.id) == saved


def test_initialization_failure_rolls_back_schema(isolated_path, monkeypatch):
    db = Database(isolated_path)
    def fail(connection):
        raise sqlite3.OperationalError("failure before first commit")
    monkeypatch.setattr(db, "_commit", fail)
    with pytest.raises(StorageError):
        db.initialize()
    connection = sqlite3.connect(isolated_path)
    try:
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='varieties'").fetchone() is None
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
    finally:
        connection.close()


def test_parent_path_unavailable(tmp_path):
    obstacle = tmp_path / "not_a_directory"
    obstacle.write_text("preserve this")
    with pytest.raises(StorageError):
        Database(obstacle / "catalog.db").initialize()
    assert obstacle.read_text() == "preserve this"
