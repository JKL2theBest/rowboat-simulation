from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .exceptions import (
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    RowboatException,
    SeatOccupiedException,
)


class SeatPosition(Enum):
    """Перечисление для позиций скамеек."""

    FRONT = "front"
    MIDDLE = "middle"
    BACK = "back"


@dataclass
class Rower:
    name: str


@dataclass
class Oar:
    id: int


@dataclass
class Seat:
    position: SeatPosition
    rower: Optional[Rower] = None

    @property
    def is_occupied(self) -> bool:
        return self.rower is not None


@dataclass
class Rowboat:
    """
    Представляет вёсельную лодку с набором методов для управления ей.
    Состояние лодки определяется флагами is_moving и is_anchor_dropped.
    """

    # Приватные атрибуты для инкапсуляции состояния
    _seats: List[Seat] = field(
        default_factory=lambda: [Seat(pos) for pos in SeatPosition]
    )
    _oars: List[Oar] = field(default_factory=lambda: [Oar(id=1), Oar(id=2)])
    _rower_with_oars: Optional[Rower] = None

    is_moving: bool = False
    is_anchor_dropped: bool = False

    def _get_seat(self, position: SeatPosition) -> Seat:
        # Поиск скамьи по позиции
        for seat in self._seats:
            if seat.position == position:
                return seat
        raise RuntimeError(f"Внутренняя ошибка: скамья {position.value} не найдена.")

    def add_rower(self, rower: Rower, position: SeatPosition) -> None:
        """Сажает гребца на указанную скамью."""
        if self.is_moving:
            raise RowboatException("Нельзя сажать гребца, когда лодка в движении.")

        if any(s.rower and s.rower.name == rower.name for s in self._seats):
            raise RowboatException(f"Гребец {rower.name} уже находится в лодке.")

        target_seat = self._get_seat(position)
        if target_seat.is_occupied:
            raise SeatOccupiedException(f"Скамья {position.value} уже занята.")

        target_seat.rower = rower

    def assign_oars_to_rower(self) -> None:
        """Назначает вёсла гребцу на средней скамье."""
        middle_seat = self._get_seat(SeatPosition.MIDDLE)
        if not middle_seat.is_occupied:
            raise OarAssignmentException(
                "Нет гребца на средней скамье для назначения вёсел."
            )

        if len(self._oars) < 2:
            raise OarAssignmentException("Недостаточно вёсел для гребли.")

        self._rower_with_oars = middle_seat.rower

    def row(self) -> None:
        """Начинает греблю."""
        if self.is_anchor_dropped:
            raise AnchorDroppedException("Якорь опущен — гребля невозможна.")

        if not self._rower_with_oars:
            raise NoRowersException("Вёсла не назначены гребцу для начала гребли.")

        self.is_moving = True

    def drop_anchor(self) -> None:
        """Бросает якорь."""
        self.is_moving = False
        self.is_anchor_dropped = True
        # Если бросили якорь, гребец освобождает вёсла
        self._rower_with_oars = None

    def raise_anchor(self) -> None:
        """Поднимает якорь."""
        self.is_anchor_dropped = False

    def get_status(self) -> dict:
        """Возвращает текущий статус лодки."""
        return {
            "is_moving": self.is_moving,
            "is_anchor_dropped": self.is_anchor_dropped,
            "seats": {
                seat.position.value: seat.rower.name if seat.rower else None
                for seat in self._seats
            },
            "rower_with_oars": (
                self._rower_with_oars.name if self._rower_with_oars else None
            ),
        }
