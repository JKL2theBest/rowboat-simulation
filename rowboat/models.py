from dataclasses import dataclass, field
from typing import Optional, List
from rowboat.exceptions import AnchorDroppedException, NoRowersException, OarAssignmentException


@dataclass
class Anchor:
    is_dropped: bool = False

    def drop(self) -> None:
        self.is_dropped = True

    def raise_up(self) -> None:
        self.is_dropped = False


@dataclass
class Seat:
    position: str  # 'front', 'middle', 'back'
    has_rower: bool = False

    def place_rower(self) -> None:
        self.has_rower = True


@dataclass
class Oar:
    id: int
    in_use: bool = False


@dataclass
class Rowboat:
    seats: List[Seat] = field(default_factory=lambda: [
        Seat(position='front'),
        Seat(position='middle'),
        Seat(position='back')
    ])
    oars: List[Oar] = field(default_factory=lambda: [Oar(id=1), Oar(id=2)])
    anchor: Anchor = field(default_factory=Anchor)
    moving: bool = False
    assigned_oars: List[Oar] = field(default_factory=list)

    def add_rower(self, position: str) -> None:
        seat = self._get_seat(position)
        seat.place_rower()

    def _get_seat(self, position: str) -> Seat:
        for seat in self.seats:
            if seat.position == position:
                return seat
        raise ValueError("Некорректная позиция скамьи")

    def assign_oars_to_middle_seat(self) -> None:
        if len(self.oars) < 2:
            raise OarAssignmentException("Недостаточно вёсел для гребли")

        # Назначаем оба весла и помечаем их как используемые
        self.assigned_oars = self.oars[:2]
        for oar in self.assigned_oars:
            oar.in_use = True

    def drop_anchor(self) -> None:
        self.anchor.drop()
        self.moving = False

    def raise_anchor(self) -> None:
        self.anchor.raise_up()

    def row(self) -> None:
        middle_seat = self._get_seat('middle')

        if self.anchor.is_dropped:
            raise AnchorDroppedException("Якорь опущен — гребля невозможна.")
        if not middle_seat.has_rower:
            raise NoRowersException("Нет гребца на средней скамье.")
        if len(self.assigned_oars) != 2 or not all(o.in_use for o in self.assigned_oars):
            raise OarAssignmentException("Не назначены оба весла для средней скамьи.")

        self.moving = True

    def get_status(self) -> dict:
        return {
            "anchor_dropped": self.anchor.is_dropped,
            "is_moving": self.moving,
            "middle_seat_has_rower": self._get_seat('middle').has_rower,
            "oars_assigned": len(self.assigned_oars),
            "oars_in_use": [o.id for o in self.assigned_oars if o.in_use]
        }
