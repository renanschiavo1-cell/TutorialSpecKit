"""Inicialização não destrutiva, esquema e integridade reais."""

import sqlite3
from dataclasses import asdict

import pytest

from potatogene.config import PROJECT_ROOT, database_path
from potatogene.data.database import Database
from potatogene.domain.errors import IncompatibleDatabaseError, StorageError
from potatogene.domain.models import DEMONSTRATIVE_SOURCE


def test_new_empty_repeated_initialization(database):
    database.initialize()
    with database.session() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM varieties").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM markers").fetchone()[0] == 0


def test_valid_empty_sqlite(isolated_path):
    sqlite3.connect(isolated_path).close()
    db = Database(isolated_path)
    db.initialize()
    db.initialize()


@pytest.mark.parametrize("sql", [
    "PRAGMA user_version = 42",
    "CREATE TABLE unknown(id INTEGER)",
    "CREATE VIEW unknown AS SELECT 1",
])
def test_unrecognized_database_preserved(isolated_path, sql):
    connection = sqlite3.connect(isolated_path)
    connection.execute(sql)
    connection.commit()
    connection.close()
    before = isolated_path.read_bytes()
    with pytest.raises(IncompatibleDatabaseError):
        Database(isolated_path).initialize()
    assert isolated_path.read_bytes() == before


def test_corrupt_file_preserved(isolated_path):
    isolated_path.write_bytes(b"not a sqlite database")
    before = isolated_path.read_bytes()
    with pytest.raises(StorageError):
        Database(isolated_path).initialize()
    assert isolated_path.read_bytes() == before


def test_missing_catalog_does_not_silently_recreate(isolated_path):
    with pytest.raises(StorageError):
        with Database(isolated_path).session():
            pass
    assert not isolated_path.exists()


def test_config_independent_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("POTATOGENE_DB_PATH")
    assert database_path() == PROJECT_ROOT / "data/potatogene.db"
    monkeypatch.setenv("POTATOGENE_DB_PATH", "temporary/catalog.db")
    assert database_path() == PROJECT_ROOT / "temporary/catalog.db"


@pytest.mark.parametrize("column,value", [
    ("name", None), ("name", ""), ("name", "x" * 101), ("name_key", ""),
    ("origin", None), ("origin", ""), ("origin", "x" * 101),
    ("skin_color", ""), ("skin_color", "x" * 51),
    ("flesh_color", ""), ("flesh_color", "x" * 51), ("size", "Gigante"),
])
def test_sql_constraints(database, variety_input, column, value):
    values = {**asdict(variety_input), "name_key": variety_input.name.casefold()}
    values[column] = value
    with pytest.raises(StorageError):
        with database.session(write=True) as connection:
            connection.execute(
                "INSERT INTO varieties(name, name_key, origin, skin_color, flesh_color, size) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                tuple(values[key] for key in ["name", "name_key", "origin", "skin_color", "flesh_color", "size"]),
            )
    with database.session() as connection:
        assert connection.execute("SELECT COUNT(*) FROM varieties").fetchone()[0] == 0


def test_bad_normalized_key_is_rejected_without_repair(database):
    with database.session(write=True) as connection:
        connection.execute(
            "INSERT INTO varieties(name,name_key,origin,skin_color,flesh_color,size) VALUES (?,?,?,?,?,?)",
            ("Demo", "wrong", "Brasil", "Amarela", "Creme", "Pequeno"),
        )
    before = database.path.read_bytes()
    with pytest.raises(IncompatibleDatabaseError):
        database.initialize()
    assert database.path.read_bytes() == before


def test_record_controls_rejected(database):
    with database.session(write=True) as connection:
        connection.execute(
            "INSERT INTO varieties(name,name_key,origin,skin_color,flesh_color,size) VALUES (?,?,?,?,?,?)",
            ("A\nB", "a\nb", "Brasil", "Amarela", "Creme", "Pequeno"),
        )
    with pytest.raises(IncompatibleDatabaseError):
        database.initialize()


def test_schema_not_repaired(database):
    with database.session(write=True) as connection:
        connection.execute("ALTER TABLE varieties ADD COLUMN extra TEXT")
    before = database.path.read_bytes()
    with pytest.raises(IncompatibleDatabaseError):
        database.initialize()
    assert database.path.read_bytes() == before


def test_marker_fk_source_and_lengths(database):
    with database.session(write=True) as connection:
        connection.execute(
            "INSERT INTO varieties(name,name_key,origin,skin_color,flesh_color,size) VALUES (?,?,?,?,?,?)",
            ("Demo", "demo", "Brasil", "Amarela", "Creme", "Pequeno"),
        )
    for params in [
        (1, "", "mk", "A", DEMONSTRATIVE_SOURCE),
        (1, "MK", "", "A", DEMONSTRATIVE_SOURCE),
        (1, "x" * 51, "mk", "A", DEMONSTRATIVE_SOURCE),
        (1, "MK", "mk", "", DEMONSTRATIVE_SOURCE),
        (1, "MK", "mk", "x" * 101, DEMONSTRATIVE_SOURCE),
        (1, "MK", "mk", "A", "Validado"),
        (1, "MK", "mk", "A", None),
    ]:
        with pytest.raises(StorageError):
            with database.session(write=True) as connection:
                connection.execute(
                    "INSERT INTO markers(variety_id,code,code_key,value,source) VALUES (?,?,?,?,?)", params,
                )


def test_foreign_key_and_cascade(database, seed_marker):
    from potatogene.domain.errors import NotFoundError
    with pytest.raises(NotFoundError):
        seed_marker(database, 99)
    with database.session(write=True) as connection:
        connection.execute(
            "INSERT INTO varieties(name,name_key,origin,skin_color,flesh_color,size) VALUES (?,?,?,?,?,?)",
            ("Demo", "demo", "Brasil", "Amarela", "Creme", "Pequeno"),
        )
    seed_marker(database, 1)
    with database.session(write=True) as connection:
        connection.execute("DELETE FROM varieties WHERE id=?", (1,))
    with database.session() as connection:
        assert connection.execute("SELECT COUNT(*) FROM markers").fetchone()[0] == 0
