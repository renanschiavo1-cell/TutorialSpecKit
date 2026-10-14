"""Contrato Streamlit do catálogo com SQLite temporário, sem navegador."""

from pathlib import Path
import sys

import pytest

from streamlit.testing.v1 import AppTest

from potatogene.data.database import Database
from potatogene.data.repositories import VarietyRepository
from potatogene.domain.errors import StorageError
from potatogene.services.varieties import VarietyService

APP = Path(__file__).resolve().parents[2] / "app.py"


@pytest.fixture(autouse=True)
def unavailable_pyarrow(monkeypatch):
    """Todos os fluxos devem funcionar mesmo sem poder importar a DLL Arrow."""
    monkeypatch.setitem(sys.modules, "pyarrow", None)


def button(at, label):
    assert not at.exception, [error.message for error in at.exception]
    matches = [widget for widget in at.button if widget.label == label]
    assert len(matches) == 1, f"Botão {label!r} ausente ou duplicado"
    return matches[0]


def selectbox(at, label):
    assert not at.exception, [error.message for error in at.exception]
    matches = [widget for widget in at.selectbox if widget.label == label]
    assert len(matches) == 1, f"Seleção {label!r} ausente ou duplicada"
    return matches[0]


def fill_form(at, name="Ágata Demo"):
    values = {"Nome": name, "Origem": "Brasil", "Cor da casca": "Amarela", "Cor da polpa": "Creme"}
    for widget in at.text_input:
        widget.set_value(values[widget.label])
    selectbox(at, "Tamanho").select("Pequeno")


def test_empty_create_no_autosave_and_rerun(database):
    at = AppTest.from_file(str(APP)).run()
    assert not at.exception
    assert any("Nenhuma variedade" in message.value for message in at.info)
    button(at, "Cadastrar variedade").click().run()
    fill_form(at)
    at.run()
    assert VarietyRepository(database).list() == []
    button(at, "Salvar").click().run()
    assert not at.exception
    assert len(VarietyRepository(database).list()) == 1
    assert any("cadastrada" in message.value for message in at.success)
    assert any("Nome: Ágata Demo" in item.value for item in at.text)
    assert not at.table
    assert not at.dataframe
    at.run()
    assert len(VarietyRepository(database).list()) == 1


def test_invalid_preserves_draft_and_correction(database):
    at = AppTest.from_file(str(APP)).run()
    button(at, "Cadastrar variedade").click().run()
    fill_form(at, name="")
    button(at, "Salvar").click().run()
    assert not at.exception
    assert any("Nome" in message.value for message in at.error)
    assert next(widget for widget in at.text_input if widget.label == "Origem").value == "Brasil"
    assert VarietyRepository(database).list() == []
    next(widget for widget in at.text_input if widget.label == "Nome").set_value("Nova")
    button(at, "Salvar").click().run()
    assert len(VarietyRepository(database).list()) == 1


def test_edit_cancel_delete_confirm(database, variety_input, seed_marker):
    service = VarietyService(VarietyRepository(database))
    saved = service.create(variety_input)
    seed_marker(database, saved.id)
    at = AppTest.from_file(str(APP)).run()
    selectbox(at, "Variedade").select(saved.id).run()
    assert any("Brasil" in item.value for item in at.text)
    button(at, "Editar").click().run()
    next(widget for widget in at.text_input if widget.label == "Origem").set_value("Outra")
    button(at, "Cancelar").click().run()
    assert service.get(saved.id).origin == "Brasil"
    assert selectbox(at, "Variedade").value == saved.id
    assert any(item.value == "Detalhes da variedade" for item in at.subheader)
    at.run()
    assert selectbox(at, "Variedade").value == saved.id
    button(at, "Editar").click().run()
    assert next(widget for widget in at.text_input if widget.label == "Origem").value == "Brasil"
    next(widget for widget in at.text_input if widget.label == "Origem").set_value("Desconhecida")
    button(at, "Salvar").click().run()
    assert service.get(saved.id).origin == "Desconhecida"
    button(at, "Excluir").click().run()
    assert any("marcadores" in item.value for item in at.warning)
    button(at, "Cancelar").click().run()
    assert len(service.list()) == 1
    assert selectbox(at, "Variedade").value == saved.id
    button(at, "Excluir").click().run()
    button(at, "Confirmar exclusão").click().run()
    assert not at.exception
    assert service.list() == []
    with database.session() as connection:
        assert connection.execute("SELECT COUNT(*) FROM markers").fetchone()[0] == 0


def test_initial_failure_retry_does_not_present_empty(monkeypatch, isolated_path):
    original = Database.initialize
    def fail(self):
        raise StorageError("Não foi possível acessar os dados. Tente novamente.")
    monkeypatch.setattr(Database, "initialize", fail)
    at = AppTest.from_file(str(APP)).run()
    assert not at.exception
    assert at.error
    assert not any("Nenhuma variedade" in message.value for message in at.info)
    assert not at.success
    monkeypatch.setattr(Database, "initialize", original)
    button(at, "Tentar novamente").click().run()
    assert not at.exception
    assert any("Nenhuma variedade" in message.value for message in at.info)


def test_write_failure_keeps_draft_and_no_success(database, monkeypatch):
    def fail(self, data):
        raise StorageError("Não foi possível salvar os dados. Tente novamente.")
    monkeypatch.setattr(VarietyService, "create", fail)
    at = AppTest.from_file(str(APP)).run()
    button(at, "Cadastrar variedade").click().run()
    fill_form(at)
    button(at, "Salvar").click().run()
    assert not at.exception
    assert at.error
    assert not at.success
    assert next(widget for widget in at.text_input if widget.label == "Nome").value == "Ágata Demo"
    assert VarietyRepository(database).list() == []


def test_duplicate_and_cancel_create_preserve_state(database, variety_input):
    saved = VarietyService(VarietyRepository(database)).create(variety_input)
    at = AppTest.from_file(str(APP)).run()
    button(at, "Cadastrar variedade").click().run()
    fill_form(at, name=" ÁGATA DEMO ")
    button(at, "Salvar").click().run()
    assert at.error
    assert not at.exception
    button(at, "Cancelar").click().run()
    assert VarietyRepository(database).list() == [saved]


def test_literal_listing_order_fields_and_reopen(database):
    from potatogene.domain.models import VarietyInput

    service = VarietyService(VarietyRepository(database))
    later = service.create(VarietyInput("Z **literal** | <b>", "Portugal", "Roxa", "Branca", "Grande"))
    service.create(VarietyInput("Ágata Demo", "Brasil", "Amarela", "Creme", "Pequeno"))
    at = AppTest.from_file(str(APP)).run()
    assert not at.exception
    expected = [
        "Nome: Z **literal** | <b>\nOrigem: Portugal\nCor da casca: Roxa\nCor da polpa: Branca\nTamanho: Grande",
        "Nome: Ágata Demo\nOrigem: Brasil\nCor da casca: Amarela\nCor da polpa: Creme\nTamanho: Pequeno",
    ]
    assert [item.value for item in at.text] == expected
    assert not at.table
    assert not at.dataframe
    selectbox(at, "Variedade").select(later.id).run()
    button(at, "Excluir").click().run()
    assert any(item.value == f"Variedade: {later.name}" for item in at.text)
    button(at, "Cancelar").click().run()
    reopened = AppTest.from_file(str(APP)).run()
    assert not reopened.exception
    assert [item.value for item in reopened.text] == expected
