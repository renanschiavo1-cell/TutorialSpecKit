"""Operações reais de variedades; marcadores somente como fixture de integridade."""

from dataclasses import replace

import pytest

from potatogene.data.database import Database
from potatogene.data.repositories import VarietyRepository
from potatogene.domain.errors import DuplicateError, NotFoundError
from potatogene.domain.models import DEMONSTRATIVE_SOURCE
from potatogene.services.varieties import VarietyService


def test_crud_sql_text_identity_order_and_cascade(database, variety_input, seed_marker):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(replace(variety_input, name="D'Ágata; DROP TABLE varieties; --"))
    marker_id = seed_marker(database, saved.id)
    alpha = service.create(replace(variety_input, name="Alpha"))
    assert [row.id for row in service.list()] == [alpha.id, saved.id]
    updated = service.update(saved.id, replace(variety_input, name="Zeta", origin="Desconhecida"))
    assert updated.id == saved.id
    with database.session() as connection:
        marker = connection.execute("SELECT * FROM markers WHERE id=?", (marker_id,)).fetchone()
        assert marker["variety_id"] == saved.id
        assert marker["source"] == DEMONSTRATIVE_SOURCE
    service.delete(saved.id)
    with database.session() as connection:
        assert connection.execute("SELECT COUNT(*) FROM markers").fetchone()[0] == 0
    new_record = service.create(replace(variety_input, name="Novo"))
    assert new_record.id > saved.id
    with pytest.raises(NotFoundError):
        service.get(saved.id)
    with pytest.raises(NotFoundError):
        service.delete(saved.id)


def test_uniqueness_enforced_after_precheck(database, variety_input):
    repo = VarietyRepository(database)
    service = VarietyService(repo)
    service.create(variety_input)
    with pytest.raises(DuplicateError):
        repo.create(variety_input, variety_input.name.casefold())
    assert len(service.list()) == 1


def test_ten_reopening_cycles(database, variety_input, seed_marker):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(variety_input)
    marker_id = seed_marker(database, saved.id)
    removed = service.create(replace(variety_input, name="Removida"))
    seed_marker(database, removed.id, "MK-02")
    service.delete(removed.id)
    saved = service.update(saved.id, replace(variety_input, origin="Desconhecida"))
    for _ in range(10):
        reopened = Database(database.path)
        reopened.initialize()
        current = VarietyService(VarietyRepository(reopened))
        assert current.list() == [saved]
        with reopened.session() as connection:
            markers = connection.execute("SELECT * FROM markers").fetchall()
            assert len(markers) == 1
            assert dict(markers[0]) == {
                "id": marker_id, "variety_id": saved.id, "code": "MK-01", "code_key": "mk-01",
                "value": "A", "source": DEMONSTRATIVE_SOURCE,
            }


def test_edit_keeps_own_name_and_other_duplicate_rejected(database, variety_input):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(variety_input)
    service.update(saved.id, replace(variety_input, name=" ÁGATA DEMO "))
    with pytest.raises(DuplicateError):
        service.create(replace(variety_input, name="ágata demo"))
