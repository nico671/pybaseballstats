from unittest.mock import patch

import matplotlib.pyplot as plt
import polars as pl
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection

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
    assert axis.get_title() == "Custom Stadium Title"
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


@pytest.fixture
def sample_statcast_data():
    """Fixture providing sample statcast data for plotting tests"""
    return pl.DataFrame(
        {
            "hc_x": [100.0, 150.0, None, 200.0],
            "hc_y": [100.0, 150.0, 175.0, 200.0],
            "plate_x": [0.5, -0.5, 1.0, -1.0],
            "plate_z": [2.0, 2.5, 3.0, 1.5],
            "sz_top": [3.5, 3.4, 3.3, 3.6],
            "sz_bot": [1.5, 1.6, 1.4, 1.5],
        }
    )


# Tests for scatter_plot_over_stadium
def test_scatter_plot_over_stadium_basic(sample_statcast_data):
    """Test basic functionality of scatter plot over stadium"""
    ax = pyb.scatter_plot_over_stadium(sample_statcast_data, "NYY")
    assert isinstance(ax, Axes)

    # Check if scatter plot was created
    scatter_plots = [c for c in ax.collections if isinstance(c, PathCollection)]
    assert len(scatter_plots) == 1

    # Check data points (excluding None values)
    assert len(scatter_plots[0].get_offsets()) == 3
    plt.close()


def test_scatter_plot_over_stadium_empty_data():
    """Test scatter plot with empty dataframe"""
    empty_data = pl.DataFrame({"hc_x": [], "hc_y": []})
    ax = pyb.scatter_plot_over_stadium(empty_data, "NYY")
    assert isinstance(ax, Axes)

    scatter_plots = [c for c in ax.collections if isinstance(c, PathCollection)]
    assert len(scatter_plots) == 1
    assert len(scatter_plots[0].get_offsets()) == 0
    plt.close()


# Tests for plot_strike_zone
def test_plot_strike_zone_default():
    """Test strike zone plot with default values"""
    ax = pyb.plot_strike_zone()
    assert isinstance(ax, Axes)

    # Check axis limits
    assert ax.get_xlim() == (-3, 3)
    assert ax.get_ylim() == (0, 5)

    # Check polygon (strike zone) exists
    assert len(ax.patches) == 1
    plt.close()


def test_plot_strike_zone_custom_values():
    """Test strike zone plot with custom values"""
    ax = pyb.plot_strike_zone(sz_top=4.0, sz_bot=1.0)
    assert isinstance(ax, Axes)

    # Check polygon vertices
    polygon = ax.patches[0]
    vertices = polygon.get_path().vertices
    assert len(vertices) == 5
    plt.close()


# Tests for plot_scatter_on_sz
def test_plot_scatter_on_sz_basic(sample_statcast_data):
    """Test basic functionality of scatter plot on strike zone"""
    ax = pyb.plot_scatter_on_sz(sample_statcast_data)
    assert isinstance(ax, Axes)

    # Check if scatter plot exists
    scatter_plots = [c for c in ax.collections if isinstance(c, PathCollection)]
    assert len(scatter_plots) == 1
    assert len(scatter_plots[0].get_offsets()) == 4
    plt.close()


def test_plot_scatter_on_sz_pandas_input(sample_statcast_data):
    """Test scatter plot with pandas DataFrame input"""
    pandas_data = sample_statcast_data.to_pandas()
    ax = pyb.plot_scatter_on_sz(pandas_data)
    assert isinstance(ax, Axes)
    plt.close()


def test_plot_scatter_on_sz_missing_columns():
    """Test scatter plot with missing required columns"""
    invalid_data = pl.DataFrame({"wrong_column": [1, 2, 3]})
    with pytest.raises(ValueError, match="must contain columns"):
        pyb.plot_scatter_on_sz(invalid_data)


def test_plot_scatter_on_sz_empty_data():
    """Test scatter plot with empty dataframe"""
    empty_data = pl.DataFrame(
        {"sz_top": [], "sz_bot": [], "plate_z": [], "plate_x": []}
    )
    with pytest.raises(ValueError, match="Dataframe is empty"):
        pyb.plot_scatter_on_sz(empty_data)


@pytest.mark.parametrize("team", ["NYY", "BOS", "LAD"])
def test_scatter_plot_over_stadium_multiple_teams(sample_statcast_data, team):
    """Test scatter plot for different teams"""
    ax = pyb.scatter_plot_over_stadium(sample_statcast_data, team)
    assert isinstance(ax, Axes)
    assert ax.get_title() == team
    plt.close()
