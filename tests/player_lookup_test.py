import pytest
from polars.testing import assert_frame_equal

import pybaseballstats as pyb


def test_illegal_player_lookup():
    with pytest.raises(ValueError):
        pyb.player_lookup(first_name=None, last_name=None)


def test_player_lookup():
    # firstname only
    df = pyb.player_lookup(first_name="mookie")
    assert len(df) > 0
    assert_frame_equal(
        pyb.player_lookup(first_name="mookie", last_name="BETTS"),
        pyb.player_lookup(first_name="MooKIE", last_name="betts"),
    )


def test_player_lookup_strip_accents():
    assert_frame_equal(
        pyb.player_lookup(first_name="mookie", last_name="betts"),
        pyb.player_lookup(first_name="möökïë", last_name="bëtts", strip_accents=True),
    )
