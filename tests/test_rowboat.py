import pytest
from rowboat.models import Rowboat
from rowboat.exceptions import (
    AnchorDroppedException,
    NoRowersException,
    OarAssignmentException,
    DuplicateRowerException,
    SeatOccupiedException,
)


def test_initial_state():
    boat = Rowboat()
    status = boat.get_status()
    assert status == {
        "anchor_dropped": False,
        "is_moving": False,
        "middle_seat_has_rower": False,
        "oars_assigned": 0,
        "oars_in_use": [],
    }


def test_drop_and_raise_anchor():
    boat = Rowboat()
    boat.drop_anchor()
    assert boat.anchor.is_dropped
    boat.raise_anchor()
    assert not boat.anchor.is_dropped


def test_add_rower_to_middle_seat():
    boat = Rowboat()
    boat.add_rower("middle")
    assert boat.get_status()["middle_seat_has_rower"] is True


def test_add_rower_to_occupied_seat_raises():
    boat = Rowboat()
    boat.add_rower("middle")
    with pytest.raises(SeatOccupiedException):
        boat.add_rower("middle")


def test_add_duplicate_rower():
    boat = Rowboat()
    boat.add_rower("middle")
    with pytest.raises(DuplicateRowerException):
        boat.add_rower("middle")  # пытаемся того же самого посадить снова


def test_assign_oars_to_middle_seat():
    boat = Rowboat()
    boat.add_rower("middle")
    boat.assign_oars_to_middle_seat()
    assert len(boat.assigned_oars) == 2
    assert all(oar.in_use for oar in boat.assigned_oars)


def test_assign_oars_twice_raises():
    boat = Rowboat()
    boat.add_rower("middle")
    boat.assign_oars_to_middle_seat()
    with pytest.raises(OarAssignmentException):
        boat.assign_oars_to_middle_seat()


def test_row_without_rower_raises():
    boat = Rowboat()
    boat.assign_oars_to_middle_seat()
    with pytest.raises(NoRowersException):
        boat.row()


def test_row_with_anchor_down_raises():
    boat = Rowboat()
    boat.add_rower("middle")
    boat.assign_oars_to_middle_seat()
    boat.drop_anchor()
    with pytest.raises(AnchorDroppedException):
        boat.row()


def test_row_without_oars_raises():
    boat = Rowboat()
    boat.add_rower("middle")
    with pytest.raises(OarAssignmentException):
        boat.row()


def test_successful_rowing_sets_status():
    boat = Rowboat()
    boat.add_rower("middle")
    boat.assign_oars_to_middle_seat()
    boat.row()
    status = boat.get_status()
    assert status["is_moving"] is True
    assert status["oars_assigned"] == 2
    assert len(status["oars_in_use"]) == 2


def test_oars_assigned_only_to_middle_seat():
    boat = Rowboat()
    boat.add_rower("front")
    with pytest.raises(OarAssignmentException):
        boat.assign_oars_to_middle_seat()  # нельзя — нет гребца в середине


def test_oars_removed_simulation():
    boat = Rowboat()
    boat.oars.pop()  # оставим только один весло
    boat.add_rower("middle")
    with pytest.raises(OarAssignmentException):
        boat.assign_oars_to_middle_seat()


def test_row_after_raise_anchor():
    boat = Rowboat()
    boat.add_rower("middle")
    boat.assign_oars_to_middle_seat()
    boat.drop_anchor()
    with pytest.raises(AnchorDroppedException):
        boat.row()
    boat.raise_anchor()
    boat.row()
    assert boat.get_status()["is_moving"] is True


def test_status_fields_consistency():
    boat = Rowboat()
    assert not boat.get_status()["is_moving"]
    boat.add_rower("middle")
    boat.assign_oars_to_middle_seat()
    boat.row()
    status = boat.get_status()
    assert status["middle_seat_has_rower"] is True
    assert status["oars_assigned"] == 2
    assert status["anchor_dropped"] is False
