"""Casos de uso testáveis sem Streamlit ou banco real."""

from potatogene.domain.errors import DuplicateError
from potatogene.domain.models import Variety, VarietyInput
from potatogene.domain.validation import normalized_key, validate_id, validate_variety


class VarietyService:
    """Regras do catálogo; dependência de dados recebida por composição simples."""

    def __init__(self, repository):
        self.repository = repository

    def create(self, value: VarietyInput) -> Variety:
        """Valide cinco campos e nome único antes de persistir."""
        clean = validate_variety(value)
        key = normalized_key(clean.name)
        if self.repository.exists_name(key):
            raise DuplicateError("Nome já cadastrado. Informe outro nome.")
        return self.repository.create(clean, key)

    def list(self) -> list[Variety]:
        """Liste registros atuais; falhas de leitura são propagadas."""
        return self.repository.list()

    def get(self, record_id: int) -> Variety:
        """Valide seleção e consulte o registro existente."""
        return self.repository.get(validate_id(record_id))

    def update(self, record_id: int, value: VarietyInput) -> Variety:
        """Edite sem alterar identidade; permita manter o próprio nome."""
        record_id = validate_id(record_id)
        clean = validate_variety(value)
        self.repository.get(record_id)
        key = normalized_key(clean.name)
        if self.repository.exists_name(key, exclude_id=record_id):
            raise DuplicateError("Nome já cadastrado. Informe outro nome.")
        return self.repository.update(record_id, clean, key)

    def delete(self, record_id: int) -> None:
        """Remova somente registro existente; confirmação pertence à UI."""
        record_id = validate_id(record_id)
        self.repository.get(record_id)
        self.repository.delete(record_id)
