from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

from .exceptions import (
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    RowboatException,
    SeatOccupiedException,
)


class SeatPosition(Enum):
    FRONT = "front"
    MIDDLE = "middle"
    BACK = "back"


class BoatState(Enum):
    IDLE = auto()  # На воде, без движения
    ROWING = auto()  # В движении (гребля)
    ANCHORED = auto()  # Стоит на якоре


@dataclass
class Rower:
    name: str


@dataclass
class Anchor:
    is_dropped: bool = False


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

    def place_rower(self, new_rower: Rower) -> None:
        if self.is_occupied:
            raise SeatOccupiedException(f"Скамья {self.position.value} уже занята.")
        self.rower = new_rower

    def remove_rower(self) -> Optional[Rower]:
        removed_rower = self.rower
        self.rower = None
        return removed_rower


@dataclass
class Rowboat:
    _seats: List[Seat] = field(
        default_factory=lambda: [Seat(pos) for pos in SeatPosition]
    )
    _oars: List[Oar] = field(default_factory=lambda: [Oar(id=1), Oar(id=2)])
    _anchor: Anchor = field(default_factory=Anchor)
    _assigned_rower: Optional[Rower] = None

    state: BoatState = BoatState.IDLE

    def _get_seat(self, position: SeatPosition) -> Seat:
        for seat in self._seats:
            if seat.position == position:
                return seat
        raise RuntimeError(f"Внутренняя ошибка: скамья {position} не найдена.")

    def _check_state(self, *allowed_states: BoatState):
        """Внутренний метод для проверки, что лодка в разрешенном состоянии."""
        if self.state not in allowed_states:
            raise RowboatException(
                f"Действие не может быть выполнено в состоянии {self.state.name}. "
                f"Разрешенные состояния: {[s.name for s in allowed_states]}."
            )

    def add_rower(self, rower: Rower, position: SeatPosition) -> None:
        """Сажает гребца на скамью, только если лодка не в движении.

        Args:
            rower: Объект гребца для посадки.
            position: Позиция скамьи (экземпляр SeatPosition).

        Raises:
            RowboatException: Если гребец уже в лодке или лодка не в состоянии IDLE.
            SeatOccupiedException: Если скамья уже занята.
        """
        self._check_state(BoatState.IDLE, BoatState.ANCHORED)

        if any(s.rower and s.rower.name == rower.name for s in self._seats):
            raise RowboatException(f"Гребец {rower.name} уже находится в лодке.")

        target_seat = self._get_seat(position)
        target_seat.place_rower(rower)

    def assign_oars_to_rower(self) -> None:
        self._check_state(BoatState.IDLE)

        middle_seat = self._get_seat(SeatPosition.MIDDLE)
        if not middle_seat.is_occupied:
            raise OarAssignmentException(
                "Нет гребца на средней скамье для назначения вёсел."
            )

        if self._assigned_rower:
            raise OarAssignmentException("Вёсла уже назначены другому гребцу.")

        if len(self._oars) < 2:
            raise OarAssignmentException("Недостаточно вёсел для гребли.")

        self._assigned_rower = middle_seat.rower

    def row(self) -> None:
        """
        Начинает греблю, переводя лодку в состояние ROWING.

        Raises:
            RowboatException: Если лодка не в состоянии IDLE.
            NoRowersException: Если гребцу не назначены вёсла.
        """
        if self.state == BoatState.ANCHORED:
            raise AnchorDroppedException("Якорь опущен — гребля невозможна.")
        if self.state == BoatState.ROWING:
            return  # Уже гребём, ничего не делаем

        if not self._assigned_rower:
            raise NoRowersException("Вёсла не назначены гребцу для начала гребли.")

        self.state = BoatState.ROWING

    def stop_rowing(self) -> None:
        if self.state == BoatState.ROWING:
            self.state = BoatState.IDLE
            self._assigned_rower = None

    def drop_anchor(self) -> None:
        if self.state == BoatState.ANCHORED:
            return

        if self.state == BoatState.ROWING:
            self.stop_rowing()

        self.state = BoatState.ANCHORED
        self._anchor.is_dropped = True

    def raise_anchor(self) -> None:
        if self.state == BoatState.IDLE:
            return
        if self.state == BoatState.ANCHORED:
            self.state = BoatState.IDLE
            self._anchor.is_dropped = False

    def get_status(self) -> dict:
        return {
            "state": self.state.name,
            "anchor_dropped": self._anchor.is_dropped,
            "seats": {
                seat.position.value: seat.rower.name if seat.rower else None
                for seat in self._seats
            },
            "rower_with_oars": (
                self._assigned_rower.name if self._assigned_rower else None
            ),
        }
