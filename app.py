"""Ponto de entrada Streamlit e composição das três camadas do catálogo."""

import logging

import streamlit as st

from potatogene.config import database_path
from potatogene.data.database import Database
from potatogene.data.repositories import VarietyRepository
from potatogene.domain.errors import PotatoGeneError
from potatogene.services.varieties import VarietyService
from potatogene.ui.feedback import show_error
from potatogene.ui.varieties import render


def main() -> None:
    """Abra dados locais e apresente catálogo; falha não simula catálogo vazio."""
    logging.basicConfig(level=logging.WARNING)
    st.set_page_config(
        page_title="PotatoGene", page_icon="🥔", layout="centered",
        menu_items={"Get Help": None, "Report a bug": None, "About": None},
    )
    st.title("PotatoGene")
    st.caption("Catálogo educacional de variedades de batata")
    try:
        database = Database(database_path())
        database.initialize()
        service = VarietyService(VarietyRepository(database))
        render(service)
    except PotatoGeneError as error:
        show_error(error)
        if st.button("Tentar novamente"):
            st.rerun()


if __name__ == "__main__":
    main()
