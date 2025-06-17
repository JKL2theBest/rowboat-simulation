import pytest
from rowboat.models import Rowboat, Rower
from rowboat.exceptions import (
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    SeatOccupiedException,
    RowboatException,
)


@pytest.fixture
def boat() -> Rowboat:
    """Возвращает новый экземпляр лодки для каждого теста."""
    return Rowboat()

@pytest.fixture
def rower_vasya() -> Rower:
    """Возвращает экземпляр гребца."""
    return Rower(name="Вася")


def test_initial_state_is_correct(boat: Rowboat):
    """Тест: начальное состояние лодки должно быть корректным."""
    status = boat.get_status()
    assert not status["is_moving"]
    assert not status["anchor_dropped"]
    assert all(rower is None for rower in status["seats"].values())
    assert not status["oars_in_use"]

def test_add_rower_successfully(boat: Rowboat, rower_vasya: Rower):
    """Тест: гребца можно успешно посадить на свободную скамью."""
    boat.add_rower(rower_vasya, "middle")
    status = boat.get_status()
    assert status["seats"]["middle"] == "Вася"

def test_add_rower_to_occupied_seat_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: нельзя посадить гребца на уже занятую скамью."""
    boat.add_rower(rower_vasya, "front")
    another_rower = Rower(name="Петя")
    
    with pytest.raises(SeatOccupiedException):
        boat.add_rower(another_rower, "front")

def test_add_same_rower_twice_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: нельзя посадить одного и того же гребца на две разные скамьи."""
    boat.add_rower(rower_vasya, "front")
    
    with pytest.raises(RowboatException):
        boat.add_rower(rower_vasya, "middle")

def test_row_with_anchor_down_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: нельзя грести, если якорь опущен."""
    boat.add_rower(rower_vasya, "middle")
    boat.assign_oars_to_rower()
    boat.drop_anchor()
    
    with pytest.raises(AnchorDroppedException):
        boat.row()
    assert not boat.is_moving

def test_row_without_rower_raises_exception(boat: Rowboat):
    """Тест: нельзя грести, если на средней скамье нет гребца."""
    with pytest.raises(NoRowersException):
        boat.row()

def test_row_without_assigned_oars_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: нельзя грести, если гребцу не выданы вёсла."""
    boat.add_rower(rower_vasya, "middle")
    
    with pytest.raises(OarAssignmentException):
        boat.row()

def test_successful_rowing_scenario(boat: Rowboat, rower_vasya: Rower):
    """Тест: полный успешный сценарий гребли."""
    boat.raise_anchor()
    boat.add_rower(rower_vasya, "middle")
    boat.assign_oars_to_rower()

    boat.row()

    status = boat.get_status()
    assert status["is_moving"]
    assert status["oars_in_use"]
    assert not status["anchor_dropped"]

def test_drop_anchor_stops_moving(boat: Rowboat, rower_vasya: Rower):
    """Тест: опускание якоря должно останавливать движение."""
    boat.add_rower(rower_vasya, "middle")
    boat.assign_oars_to_rower()
    boat.row()
    assert boat.is_moving

    boat.drop_anchor()

    status = boat.get_status()
    assert not status["is_moving"]
    assert status["anchor_dropped"]
    assert not status["oars_in_use"]