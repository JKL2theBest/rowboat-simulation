from dataclasses import dataclass, field
from typing import List, Optional
from .exceptions import (
    RowboatException, # Хорошая практика - иметь общее исключение
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    SeatOccupiedException,
)

@dataclass
class Rower:
    name: str

@dataclass
class Anchor:
    is_dropped: bool = False

    def drop(self) -> None:
        if self.is_dropped:
            return
        self.is_dropped = True

    def raise_up(self) -> None:
        if not self.is_dropped:
            return
        self.is_dropped = False

@dataclass
class Oar:
    id: int
    is_in_use: bool = False

@dataclass
class Seat:
    position: str  # 'front', 'middle', 'back'
    rower: Optional[Rower] = None

    @property
    def is_occupied(self) -> bool:
        return self.rower is not None

    def place_rower(self, new_rower: Rower) -> None:
        if self.is_occupied:
            raise SeatOccupiedException(f"Скамья {self.position} уже занята гребцом {self.rower.name}.")
        self.rower = new_rower

    def remove_rower(self) -> Optional[Rower]:
        if not self.is_occupied:
            return None
        removed_rower = self.rower
        self.rower = None
        return removed_rower

@dataclass
class Rowboat:
    SEAT_POSITIONS = ('front', 'middle', 'back')

    seats: List[Seat] = field(default_factory=lambda: [Seat(pos) for pos in Rowboat.SEAT_POSITIONS])
    oars: List[Oar] = field(default_factory=lambda: [Oar(id=1), Oar(id=2)])
    anchor: Anchor = field(default_factory=Anchor)
    is_moving: bool = False

    def _get_seat(self, position: str) -> Seat:
        if position not in self.SEAT_POSITIONS:
            raise ValueError(f"Некорректная позиция скамьи: {position}. Доступные: {self.SEAT_POSITIONS}")
        for seat in self.seats:
            if seat.position == position:
                return seat
        # Эта строка теоретически недостижима
        raise RuntimeError("Внутренняя ошибка: скамья не найдена.")

    def add_rower(self, rower: Rower, position: str) -> None:
        for seat in self.seats:
            if seat.rower and seat.rower.name == rower.name:
                raise RowboatException(f"Гребец {rower.name} уже находится в лодке на скамье {seat.position}.")

        target_seat = self._get_seat(position)
        target_seat.place_rower(rower)

    def assign_oars_to_rower(self) -> None:
        middle_seat = self._get_seat('middle')
        if not middle_seat.is_occupied:
            raise OarAssignmentException("Нет гребца на средней скамье для назначения вёсел.")

        if any(oar.is_in_use for oar in self.oars):
            raise OarAssignmentException("Вёсла уже назначены.")

        if len(self.oars) < 2:
            raise OarAssignmentException("Недостаточно вёсел для гребли.")

        for oar in self.oars:
            oar.is_in_use = True

    def row(self) -> None:
        if self.anchor.is_dropped:
            raise AnchorDroppedException("Якорь опущен — гребля невозможна.")

        middle_seat = self._get_seat('middle')
        if not middle_seat.is_occupied:
            raise NoRowersException("Нет гребца на средней скамье, чтобы грести.")

        # Проверяем, что оба весла "взяты"
        if not all(oar.is_in_use for oar in self.oars):
            raise OarAssignmentException("Вёсла не назначены гребцу.")

        self.is_moving = True

    def stop_rowing(self) -> None:
        self.is_moving = False
        for oar in self.oars:
            oar.is_in_use = False

    def drop_anchor(self) -> None:
        self.anchor.drop()
        if self.is_moving:
            self.stop_rowing()

    def raise_anchor(self) -> None:
        self.anchor.raise_up()
        
    def get_status(self) -> dict:
        middle_seat = self._get_seat('middle')
        return {
            "is_moving": self.is_moving,
            "anchor_dropped": self.anchor.is_dropped,
            "seats": {
                seat.position: seat.rower.name if seat.rower else None 
                for seat in self.seats
            },
            "oars_in_use": all(o.is_in_use for o in self.oars),
        }