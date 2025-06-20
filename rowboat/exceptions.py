class RowboatException(Exception):
    """Базовое исключение."""


class AnchorDroppedException(RowboatException):
    """Попытка грести с опущенным якорем."""


class NoRowersException(RowboatException):
    """Попытка грести без гребца или назначенных вёсел."""


class OarAssignmentException(RowboatException):
    """Ошибка назначения вёсел."""


class SeatOccupiedException(RowboatException):
    """Исключение при попытке посадить гребца на занятую скамью."""
