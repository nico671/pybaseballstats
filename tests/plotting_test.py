from unittest.mock import patch

import matplotlib.pyplot as plt
import polars as pl
import pytest

import pybaseballstats as pyb


@pytest.fixture
def mock_stadium_data():
    """Fixture providing mock stadium data"""
    return pl.DataFrame(
        {
            "team": ["NYY", "NYY", "NYY"],
            "segment": [1, 1, 2],
            "x": [100, 150, 200],
            "y": [100, 150, 200],
        }
    )


def test_plot_stadium_basic():
    """Test basic stadium plotting functionality"""
    axis = pyb.plot_stadium("NYY")
    assert isinstance(axis, plt.Axes)
    assert axis.get_title() == "NYY"
    plt.close()


def test_plot_stadium_dimensions():
    """Test stadium plot dimensions"""
    axis = pyb.plot_stadium("NYY")
    assert axis.get_xlim() == (0, 250)
    assert axis.get_ylim() == (-250, 0)
    plt.close()


def test_plot_stadium_invalid_team():
    """Test plotting with invalid team name"""
    axis = pyb.plot_stadium("INVALID")
    # Should create empty plot with no patches
    assert len(axis.patches) == 0
    plt.close()


@pytest.mark.parametrize("team", ["NYY", "BOS", "LAD", "CHC"])
def test_plot_stadium_multiple_teams(team):
    """Test plotting for different teams"""
    axis = pyb.plot_stadium(team)
    assert isinstance(axis, plt.Axes)
    assert axis.get_title() == team
    plt.close()


def test_plot_stadium_file_not_found():
    """Test handling of missing stadium data file"""
    with patch("polars.read_csv") as mock_read:
        mock_read.side_effect = FileNotFoundError
        with pytest.raises(FileNotFoundError):
            pyb.plot_stadium("NYY")


def test_plot_stadium_custom_title():
    """Test plotting with custom title"""
    custom_title = "Custom Stadium Title"
    axis = pyb.plot_stadium("NYY", title=custom_title)
    assert axis.get_title() == "NYY"  # Current behavior - title parameter is unused
    plt.close()


@pytest.mark.parametrize("scale", [1.0, 1.5, 2.0])
def test_plot_stadium_scaling(scale, monkeypatch):
    """Test stadium plotting with different scales"""
    monkeypatch.setattr("pybaseballstats.plotting.STADIUM_SCALE", scale)
    axis = pyb.plot_stadium("NYY")
    assert isinstance(axis, plt.Axes)
    plt.close()


def test_plot_stadium_figure_size():
    """Test stadium figure size"""
    axis = pyb.plot_stadium("NYY")
    fig = axis.figure
    assert fig.get_size_inches().tolist() == [5, 5]
    plt.close()
