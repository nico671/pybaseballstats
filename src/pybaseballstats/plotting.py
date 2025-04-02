from pathlib import Path

import matplotlib
import pandas as pd
import polars as pl
from matplotlib import patches
from matplotlib import pyplot as plt

STADIUM_SCALE = 2.495 / 2.33

# heavy inspiration from pybaseball package
# https://github.com/jldbc/pybaseball/blob/master/pybaseball/plotting.py


# TODO: make the stadium plot more general and add docstrings for all functions
# TODO: usage docs
def plot_stadium(team: str, title: str = None):
    # Construct absolute path to the CSV file
    csv_path = Path(__file__).parent / "data" / "mlbstadiums.csv"
    try:
        stad_data = pl.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"CSV file '{csv_path}' not found. Please ensure the file exists at the correct path."
        )
    filtered_stad_data = stad_data.filter(pl.col("team") == team)
    filtered_stad_data = filtered_stad_data.with_columns(
        [
            # sign * ((coord - center) * scale + center)
            (1 * ((pl.col("x") - 125) * STADIUM_SCALE + 125)).alias("x"),
            (-1 * ((pl.col("y") - 0) * STADIUM_SCALE + 0)).alias("y"),
        ]
    )
    stadium = plt.figure()
    stadium.set_size_inches(5, 5)
    axis = stadium.add_axes([0, 0, 1, 1], frameon=False, aspect=1)
    axis.set_xlim(0, 250)
    axis.set_ylim(-250, 0)

    segments = (
        filtered_stad_data.select(pl.col("segment").unique()).to_series().to_list()
    )
    for seg in segments:
        verts = (
            filtered_stad_data.filter(pl.col("segment") == seg)
            .select(pl.col("x"), pl.col("y"))
            .to_numpy()
        )
        path = matplotlib.path.Path(verts)
        patch = patches.PathPatch(path, facecolor="none", edgecolor="black", lw=2)
        axis.add_patch(patch)
    if title:
        plt.title(title)
    else:
        plt.title(team)
    return axis


def scatter_plot_over_stadium(data, team_stadium):
    base = plot_stadium(team_stadium)
    data = data.filter(pl.col("hc_x").is_not_null() & pl.col("hc_y").is_not_null())
    data = data.with_columns(
        [
            (pl.col("hc_y").cast(pl.Float64) * -1).alias("hc_y"),
            pl.col("hc_x").cast(pl.Float64).alias("hc_x"),
        ]
    )
    scatters = []
    scatters.append(
        base.scatter(
            data["hc_x"].to_numpy(),
            data["hc_y"].to_numpy(),
            c="red",
            s=4,
        )
    )
    return base


def plot_strike_zone(sz_top=3.389, sz_bot=1.586):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    # Set the aspect ratio to be equal
    ax.set_xlim(-3, 3)
    ax.set_ylim(0, 5)
    coords = [
        # 17 inches wide, heights taken from average strike zone top and bottom from statcast data
        (8.5 / 12, sz_top),
        (8.5 / 12, sz_bot),
        (-8.5 / 12, sz_bot),
        (-8.5 / 12, sz_top),
    ]
    home = plt.Polygon(coords, edgecolor="black", facecolor="none")
    ax.add_patch(home)
    return ax


def plot_scatter_on_sz(data):
    if (
        "sz_top" not in data.columns
        or "sz_bot" not in data.columns
        or "plate_z" not in data.columns
        or "plate_x" not in data.columns
    ):
        raise ValueError(
            "Dataframe must contain columns 'sz_top', 'sz_bot', 'plate_z', and 'plate_x'"
        )
    if data.shape[0] == 0:
        raise ValueError("Dataframe is empty")
    if type(data) is pd.DataFrame:
        data = pl.DataFrame(data)
    data = data.filter(
        pl.col("plate_z").is_not_null() & pl.col("plate_x").is_not_null()
    )
    mean_sz_top = data.select(pl.col("sz_top").mean()).item()
    mean_sz_bot = data.select(pl.col("sz_bot").mean()).item()
    sz = plot_strike_zone(mean_sz_top, mean_sz_bot)
    data = data.with_columns(
        [
            pl.col("plate_z").cast(pl.Float64).alias("plate_z"),
            pl.col("plate_x").cast(pl.Float64).alias("plate_x"),
        ]
    )
    sz.scatter(data["plate_x"].to_numpy(), data["plate_z"].to_numpy(), c="red", s=4)
    return sz
