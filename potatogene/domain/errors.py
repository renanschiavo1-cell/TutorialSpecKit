"""Erros públicos e mensagens de domínio em português."""


class PotatoGeneError(Exception):
    """Base para falhas esperadas que podem ser apresentadas sem traceback."""


class ValidationError(PotatoGeneError):
    """Erros por nome de campo; a UI pode preservar o restante do rascunho."""

    def __init__(self, fields: dict[str, str]):
        self.fields = fields
        super().__init__("; ".join(fields.values()))


class DuplicateError(PotatoGeneError):
    """Nome ou código já utilizado no escopo correspondente."""


class NotFoundError(PotatoGeneError):
    """Registro excluído ou inexistente."""


class InvalidComparisonError(PotatoGeneError):
    """Seleção de comparação inválida; definida somente para o contrato futuro."""


class StorageError(PotatoGeneError):
    """Leitura/gravação indisponível, sem confirmação de sucesso."""


class IncompatibleDatabaseError(StorageError):
    """Esquema, versão ou conteúdo não reconhecido; arquivo deve ser preservado."""
