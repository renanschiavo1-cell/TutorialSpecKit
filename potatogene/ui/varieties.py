"""Telas do catálogo: coleta e apresentação, sem SQL nem regras de domínio."""

import streamlit as st

from potatogene.domain.errors import NotFoundError, PotatoGeneError
from potatogene.domain.models import SIZES, VarietyInput
from potatogene.ui.feedback import show_error

LABELS = {
    "name": "Nome", "origin": "Origem", "skin_color": "Cor da casca",
    "flesh_color": "Cor da polpa", "size": "Tamanho",
}


def _request_screen(mode: str, record=None, message: str | None = None) -> None:
    # Consumido ANTES de criar widgets no próximo ciclo, nunca depois de renderizá-los.
    st.session_state["pending_screen"] = {"mode": mode, "record": record, "message": message}


def _consume_screen() -> None:
    request = st.session_state.pop("pending_screen", None)
    if request is None:
        return
    for key in list(st.session_state):
        if key.startswith("variety_form:"):
            del st.session_state[key]
    st.session_state["screen"] = request["mode"]
    record = request["record"]
    st.session_state["target_id"] = record.id if record else None
    if record is not None:
        st.session_state["selected_variety"] = record.id
    elif request["mode"] == "list":
        st.session_state.pop("selected_variety", None)
    if request["mode"] == "edit" and record is not None:
        for field in LABELS:
            st.session_state[f"variety_form:edit:{record.id}:{field}"] = getattr(record, field)
    if request["message"]:
        st.session_state["flash"] = request["message"]


def _form(service, mode: str) -> None:
    record_id = st.session_state.get("target_id")
    prefix = f"variety_form:{mode}:{record_id}"
    st.subheader("Editar variedade" if mode == "edit" else "Cadastrar variedade")
    with st.form(f"{prefix}:form", clear_on_submit=False):
        fields = {
            field: st.text_input(label, key=f"{prefix}:{field}")
            for field, label in LABELS.items() if field != "size"
        }
        size = st.selectbox(
            "Tamanho", SIZES, index=None, placeholder="Selecione um tamanho", key=f"{prefix}:size",
        )
        save = st.form_submit_button("Salvar")
        cancel = st.form_submit_button("Cancelar")
    if cancel:
        current = service.get(record_id) if mode == "edit" else None
        _request_screen("list", current)
        st.rerun()
    if save:
        try:
            value = VarietyInput(**fields, size=size)
            saved = service.update(record_id, value) if mode == "edit" else service.create(value)
        except PotatoGeneError as error:
            show_error(error)
        else:
            message = "Variedade atualizada com sucesso." if mode == "edit" else "Variedade cadastrada com sucesso."
            _request_screen("list", saved, message)
            st.rerun()


def _delete(service) -> None:
    record_id = st.session_state.get("target_id")
    try:
        current = service.get(record_id)
    except NotFoundError as error:
        show_error(error)
        st.button("Voltar às variedades", on_click=_request_screen, args=("list",))
        return
    st.subheader("Excluir variedade")
    st.text(f"Variedade: {current.name}")
    st.warning("Os marcadores desta variedade também serão excluídos.")
    confirm = st.button("Confirmar exclusão", type="primary")
    st.button("Cancelar", on_click=_request_screen, args=("list", current))
    if confirm:
        try:
            service.delete(current.id)
        except PotatoGeneError as error:
            show_error(error)
        else:
            _request_screen("list", message="Variedade excluída com sucesso.")
            st.rerun()


def render(service) -> None:
    """Apresente registros atuais; somente submissão/confirmar pode persistir."""
    _consume_screen()
    st.header("Variedades")
    flash = st.session_state.pop("flash", None)
    if flash:
        st.success(flash)
    mode = st.session_state.get("screen", "list")
    if mode in {"create", "edit"}:
        _form(service, mode)
        return
    if mode == "delete":
        _delete(service)
        return

    # Uma falha é propagada: o app mostra erro e Tentar novamente, não uma lista vazia.
    records = service.list()
    st.button("Cadastrar variedade", on_click=_request_screen, args=("create",), type="primary")
    if not records:
        st.info("Nenhuma variedade cadastrada. Cadastre a primeira variedade para começar.")
        return
    # Texto literal preserva os dados e não usa a serialização Arrow de tabelas.
    for record in records:
        st.text("\n".join(
            f"{label}: {getattr(record, field)}" for field, label in LABELS.items()
        ))
    by_id = {record.id: record for record in records}
    if st.session_state.get("selected_variety") not in by_id:
        st.session_state.pop("selected_variety", None)
    selected = st.selectbox(
        "Variedade", list(by_id), index=None, placeholder="Selecione uma variedade",
        format_func=lambda record_id: by_id[record_id].name, key="selected_variety",
    )
    if selected is None:
        return
    record = service.get(selected)
    st.subheader("Detalhes da variedade")
    for field, label in LABELS.items():
        st.text(f"{label}: {getattr(record, field)}")
    st.button("Editar", on_click=_request_screen, args=("edit", record))
    st.button("Excluir", on_click=_request_screen, args=("delete", record))
