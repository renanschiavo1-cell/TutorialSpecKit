"""Contrato de negócio com repositório em memória."""

from dataclasses import replace

import pytest

from potatogene.domain.errors import DuplicateError, NotFoundError, ValidationError
from potatogene.services.varieties import VarietyService


def test_crud_without_database_or_interface(memory_repository, variety_input):
    service = VarietyService(memory_repository)
    assert service.list() == []
    saved = service.create(variety_input)
    assert service.get(saved.id) == saved
    edited = service.update(saved.id, replace(variety_input, origin="Desconhecida"))
    assert edited.id == saved.id
    assert edited.origin == "Desconhecida"
    assert len(service.list()) == 1
    service.delete(saved.id)
    assert service.list() == []
    with pytest.raises(NotFoundError):
        service.get(saved.id)


def test_unicode_duplicate_and_own_name(memory_repository, variety_input):
    service = VarietyService(memory_repository)
    saved = service.create(replace(variety_input, name="Straße"))
    with pytest.raises(DuplicateError):
        service.create(replace(variety_input, name=" STRASSE "))
    own = service.update(saved.id, replace(variety_input, name=" STRASSE "))
    assert own.id == saved.id
    assert own.name == "STRASSE"


def test_rename_to_other_name_and_sort(memory_repository, variety_input):
    service = VarietyService(memory_repository)
    beta = service.create(replace(variety_input, name="beta"))
    alpha = service.create(replace(variety_input, name="Alpha"))
    assert [row.id for row in service.list()] == [alpha.id, beta.id]
    with pytest.raises(DuplicateError):
        service.update(beta.id, replace(variety_input, name=" ALPHA "))
    assert service.get(beta.id) == beta


def test_invalid_never_reaches_repository(memory_repository, variety_input):
    service = VarietyService(memory_repository)
    with pytest.raises(ValidationError):
        service.create(replace(variety_input, name=""))
    assert memory_repository.records == {}
    with pytest.raises(ValidationError):
        service.get(True)
    for operation in [lambda: service.update(999, variety_input), lambda: service.delete(999)]:
        with pytest.raises(NotFoundError):
            operation()


def test_invalid_update_preserves_record(memory_repository, variety_input):
    service = VarietyService(memory_repository)
    saved = service.create(variety_input)
    with pytest.raises(ValidationError):
        service.update(saved.id, replace(variety_input, size=None))
    assert service.get(saved.id) == saved
