class RowboatException(Exception):
    """Базовое исключение для лодки."""


class AnchorDroppedException(RowboatException):
    """Попытка грести с опущенным якорем."""


class NoRowersException(RowboatException):
    """Попытка грести без гребца."""


class OarAssignmentException(RowboatException):
    """Ошибка назначения вёсел."""


class DuplicateRowerException(Exception):
    """Исключение для повторного добавления гребца на скамью."""
    pass


class SeatOccupiedException(RowboatException):
    """Исключение при попытке посадить гребца на занятую скамью."""
    pass
