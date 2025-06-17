class RowboatException(Exception):
    """Базовое исключение для лодки."""


class AnchorDroppedException(RowboatException):
    """Попытка грести с опущенным якорем."""


class NoRowersException(RowboatException):
    """Попытка грести без гребца."""


class OarAssignmentException(RowboatException):
    """Ошибка назначения вёсел."""
