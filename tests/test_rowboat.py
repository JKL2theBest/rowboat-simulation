import pytest

from rowboat.exceptions import (
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    RowboatException,
    SeatOccupiedException,
)
from rowboat.models import BoatState, Rowboat, Rower, SeatPosition


@pytest.fixture
def boat() -> Rowboat:
    return Rowboat()


@pytest.fixture
def rower_vasya() -> Rower:
    return Rower(name="Вася")


def test_initial_state_is_idle(boat: Rowboat):
    """Тест: Изначально лодка должна быть в состоянии IDLE."""
    status = boat.get_status()
    assert boat.state == BoatState.IDLE
    assert status["state"] == "IDLE"
    assert not status["anchor_dropped"]
    assert all(rower is None for rower in status["seats"].values())
    assert status["rower_with_oars"] is None


@pytest.mark.parametrize(
    "position", [SeatPosition.FRONT, SeatPosition.MIDDLE, SeatPosition.BACK]
)
def test_add_rower_successfully_to_any_seat(
    boat: Rowboat, rower_vasya: Rower, position: SeatPosition
):
    """Тест: Гребца можно успешно посадить на любую свободную скамью."""
    boat.add_rower(rower_vasya, position)
    assert boat.get_status()["seats"][position.value] == "Вася"


def test_successful_rowing_scenario(boat: Rowboat, rower_vasya: Rower):
    """Тест: Полный успешный сценарий: посадка, назначение вёсел, гребля."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.row()

    assert boat.state == BoatState.ROWING
    status = boat.get_status()
    assert status["state"] == "ROWING"
    assert status["rower_with_oars"] == "Вася"


def test_add_rower_to_occupied_seat_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя посадить гребца на уже занятую скамью."""
    boat.add_rower(rower_vasya, SeatPosition.FRONT)
    another_rower = Rower(name="Петя")

    with pytest.raises(SeatOccupiedException):
        boat.add_rower(another_rower, SeatPosition.FRONT)


def test_add_same_rower_twice_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя посадить одного и того же гребца дважды."""
    boat.add_rower(rower_vasya, SeatPosition.FRONT)

    with pytest.raises(RowboatException, match="уже находится в лодке"):
        boat.add_rower(rower_vasya, SeatPosition.MIDDLE)


def test_row_when_anchored_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя грести, если якорь опущен."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.drop_anchor()

    assert boat.state == BoatState.ANCHORED
    with pytest.raises(AnchorDroppedException):
        boat.row()


def test_row_without_assigned_oars_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя грести, если вёсла не назначены гребцу."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)

    with pytest.raises(NoRowersException):
        boat.row()


def test_assign_oars_without_rower_on_middle_seat_raises_exception(
    boat: Rowboat, rower_vasya: Rower
):
    """Тест: Нельзя назначить вёсла, если на средней скамье нет гребца."""
    boat.add_rower(rower_vasya, SeatPosition.FRONT)

    with pytest.raises(OarAssignmentException, match="Нет гребца на средней скамье"):
        boat.assign_oars_to_rower()


def test_drop_anchor_stops_rowing(boat: Rowboat, rower_vasya: Rower):
    """Тест: Опускание якоря останавливает движение и меняет состояние на ANCHORED."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.row()
    assert (
        boat.state == BoatState.ROWING
    )  # Логика stop_rowing вызывается внутри drop_anchor, но state меняется на ANCHORED

    boat.drop_anchor()

    assert boat.state == BoatState.ANCHORED
    assert boat.get_status()["anchor_dropped"] is True


def test_raise_anchor_changes_state_to_idle(boat: Rowboat):
    """Тест: Поднятие якоря переводит лодку из состояния ANCHORED в IDLE."""
    boat.drop_anchor()
    assert boat.state == BoatState.ANCHORED

    boat.raise_anchor()

    assert boat.state == BoatState.IDLE
    assert boat.get_status()["anchor_dropped"] is False
