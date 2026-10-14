"""Apresentação de erros esperados em português, sem rastreamentos técnicos."""

import logging

import streamlit as st

from potatogene.domain.errors import PotatoGeneError, ValidationError

LOGGER = logging.getLogger(__name__)


def show_error(error: PotatoGeneError) -> None:
    """Mostre campos inválidos ou uma orientação, mantendo o rascunho na sessão."""
    if isinstance(error, ValidationError):
        for message in error.fields.values():
            st.error(message)
    else:
        st.error(str(error))
    LOGGER.warning("Operação não concluída: %s", type(error).__name__, exc_info=True)
