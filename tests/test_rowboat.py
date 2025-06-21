import pytest

from rowboat.exceptions import (
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    RowboatException,
    SeatOccupiedException,
)
from rowboat.models import Rowboat, Rower, SeatPosition


@pytest.fixture
def boat() -> Rowboat:
    """Чистый экземпляр лодки для каждого теста."""
    return Rowboat()


@pytest.fixture
def rower_vasya() -> Rower:
    """Экземпляр гребца 'Вася'."""
    return Rower(name="Вася")


def test_initial_state_is_correct(boat: Rowboat):
    """Тест: Изначально лодка должна быть на воде, не двигаться, с поднятым якорем."""
    status = boat.get_status()

    assert not boat.is_moving
    assert not boat.is_anchor_dropped
    assert status["is_moving"] is False
    assert status["is_anchor_dropped"] is False
    assert all(rower is None for rower in status["seats"].values())
    assert status["rower_with_oars"] is None


@pytest.mark.parametrize("position", list(SeatPosition))
def test_add_rower_successfully_to_any_seat(
    boat: Rowboat, rower_vasya: Rower, position: SeatPosition
):
    """Тест: Гребца можно успешно посадить на любую свободную скамью."""
    boat.add_rower(rower_vasya, position)

    assert boat.get_status()["seats"][position.value] == "Вася"


def test_add_rower_to_occupied_seat_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя посадить гребца на уже занятую скамью."""
    boat.add_rower(rower_vasya, SeatPosition.FRONT)
    another_rower = Rower(name="Петя")

    with pytest.raises(SeatOccupiedException):
        boat.add_rower(another_rower, SeatPosition.FRONT)


def test_add_same_rower_twice_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя посадить одного и того же гребца на две разные скамьи."""
    boat.add_rower(rower_vasya, SeatPosition.FRONT)

    with pytest.raises(RowboatException, match="уже находится в лодке"):
        boat.add_rower(rower_vasya, SeatPosition.MIDDLE)


def test_add_rower_while_moving_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя сажать гребца, когда лодка в движении."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.row()
    assert boat.is_moving

    another_rower = Rower(name="Петя")
    with pytest.raises(RowboatException, match="лодка в движении"):
        boat.add_rower(another_rower, SeatPosition.FRONT)


def test_assign_oars_without_rower_on_middle_seat_raises_exception(
    boat: Rowboat, rower_vasya: Rower
):
    """Тест: Нельзя назначить вёсла, если на средней скамье нет гребца."""
    boat.add_rower(rower_vasya, SeatPosition.FRONT)

    with pytest.raises(OarAssignmentException, match="Нет гребца на средней скамье"):
        boat.assign_oars_to_rower()


def test_assign_oars_with_insufficient_oars_raises_exception(
    boat: Rowboat, rower_vasya: Rower
):
    """Тест: Нельзя назначить вёсла, если их в лодке меньше двух."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat._oars.pop()  # Имитация потери весла
    boat._oars.pop()

    with pytest.raises(OarAssignmentException, match="Недостаточно вёсел"):
        boat.assign_oars_to_rower()


def test_row_when_anchored_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя грести, если якорь опущен."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.drop_anchor()

    with pytest.raises(AnchorDroppedException):
        boat.row()

    assert not boat.is_moving


def test_row_without_assigned_oars_raises_exception(boat: Rowboat, rower_vasya: Rower):
    """Тест: Нельзя грести, если вёсла не были назначены гребцу."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)

    with pytest.raises(NoRowersException, match="Вёсла не назначены"):
        boat.row()


def test_drop_anchor_stops_rowing_and_releases_oars(boat: Rowboat, rower_vasya: Rower):
    """Тест: Опускание якоря останавливает движение и освобождает вёсла."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.row()
    assert boat.is_moving
    assert boat.get_status()["rower_with_oars"] is not None

    boat.drop_anchor()

    status = boat.get_status()
    assert not status["is_moving"]
    assert status["is_anchor_dropped"]
    assert status["rower_with_oars"] is None


def test_raise_anchor_works_correctly(boat: Rowboat):
    """Тест: Поднятие якоря меняет его статус."""
    boat.drop_anchor()
    assert boat.is_anchor_dropped

    boat.raise_anchor()

    assert not boat.is_anchor_dropped


def test_idempotency_of_anchor_actions(boat: Rowboat):
    """Тест: Повторные вызовы методов якоря не вызывают ошибок и не меняют состояние."""
    boat.drop_anchor()
    status_after_first_drop = boat.get_status()
    boat.drop_anchor()
    assert boat.get_status() == status_after_first_drop

    boat.raise_anchor()
    status_after_first_raise = boat.get_status()
    boat.raise_anchor()
    assert boat.get_status() == status_after_first_raise


def test_system_full_journey_scenario(boat: Rowboat, rower_vasya: Rower):
    """Тест: Эмуляция полного 'путешествия' с греблей, остановкой и возобновлением."""
    boat.add_rower(rower_vasya, SeatPosition.MIDDLE)
    boat.assign_oars_to_rower()
    boat.row()
    assert boat.is_moving and boat.get_status()["rower_with_oars"] == "Вася"

    boat.drop_anchor()
    assert boat.is_anchor_dropped and not boat.is_moving
    assert boat.get_status()["rower_with_oars"] is None

    boat.raise_anchor()
    assert not boat.is_anchor_dropped

    boat.assign_oars_to_rower()
    boat.row()
    assert boat.is_moving and boat.get_status()["rower_with_oars"] == "Вася"


def test_system_max_load_scenario(boat: Rowboat):
    """Тест: Проверка системы при максимальной загрузке гребцами."""
    rower1, rower2, rower3 = Rower("Петя"), Rower("Вася"), Rower("Коля")

    boat.add_rower(rower1, SeatPosition.FRONT)
    boat.add_rower(rower2, SeatPosition.MIDDLE)
    boat.add_rower(rower3, SeatPosition.BACK)

    status = boat.get_status()
    assert status["seats"]["front"] == "Петя"
    assert status["seats"]["middle"] == "Вася"
    assert status["seats"]["back"] == "Коля"

    # Грести может только тот, кто посередине
    boat.assign_oars_to_rower()
    boat.row()

    assert boat.is_moving
