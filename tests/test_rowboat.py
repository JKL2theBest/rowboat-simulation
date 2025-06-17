import pytest
from rowboat.models import Rowboat
from rowboat.exceptions import AnchorDroppedException, NoRowersException

def test_row_without_anchor():
    boat = Rowboat()
    boat.raise_anchor()
    boat.seats[1].has_rower = True
    boat.row()
    assert boat.moving is True

def test_row_with_anchor_dropped():
    boat = Rowboat()
    boat.seats[1].has_rower = True
    boat.drop_anchor()
    with pytest.raises(AnchorDroppedException):
        boat.row()

def test_no_rowers():
    boat = Rowboat()
    boat.raise_anchor()
    with pytest.raises(NoRowersException):
        boat.row()
