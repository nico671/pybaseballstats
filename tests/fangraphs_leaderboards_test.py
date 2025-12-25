from datetime import datetime

import polars as pl
import pytest

import pybaseballstats.fangraphs_leaderboards as fg


def test_fangraphs_batting_leaderboard_date_season_badinput_together():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=2021,
            start_date=None,
            end_date="2021-06-30",
        )
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=2020,
            end_season=None,
            start_date="2020-04-01",
            end_date=None,
        )


def test_fangraphs_batting_leaderboard_season_badinput():
    # start_season < 1871
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=1800,
            end_season=2021,
        )
    # start_season > current_year
    current_year = datetime.now().year
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=current_year + 1,
            end_season=current_year + 2,
        )
    # end_season > current_year with start_season none so single year search with end_season
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=current_year + 1,
        )
    # end_season < 1871 with start_season none so single year search with end_season
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=1800,
        )
    # both none (shouldnt ever be reached but just in case)
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
        )
    # start_season < 1871 with end_season valid
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=1800,
            end_season=2000,
        )

    # start_season > current_year with end_season valid
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=current_year + 1,
            end_season=2022,
        )
    # end_season < 1871 with start_season valid
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=2000,
            end_season=1800,
        )
    # end_season > current_year with start_season valid
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=2020,
            end_season=current_year + 1,
        )
    # end_season < start_season
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=2022,
            end_season=2020,
        )


def test_fangraphs_batting_leaderboard_dates_badinput():
    # start_date none and end_date valid
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
            start_date=None,
            end_date="2021-06-30",
        )
    # start_date > end_date
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
            start_date="2021-07-01",
            end_date="2021-06-30",
        )
    # start_date year < 1871
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
            start_date="1800-06-30",
            end_date="2021-06-30",
        )
    # start_date year > current_year
    current_year = datetime.now().year
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
            start_date=f"{current_year + 1}-01-01",
            end_date="2021-06-30",
        )
    # end_date year < 1871
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
            start_date="2020-01-01",
            end_date="1800-06-30",
        )
    # end_date year > current_year
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            start_season=None,
            end_season=None,
            start_date="2020-01-01",
            end_date=f"{current_year + 1}-01-01",
        )


def test_fangraphs_batting_leaderboard_position_badinput():
    # only need to check case where type != FangraphsBattingPosTypes
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            position="INVALID_POSITION",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_season_type_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            season_type="REGULAR_SEASON",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_split_seasons_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            split_seasons="yes",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_league_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            league="AL",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_min_pa_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            min_pa=-100,
        )
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            min_pa="qualified",
        )


def test_fangraphs_batting_leaderboard_stat_split_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            stat_split="individual",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_team_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            team="Yankees",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_batter_handedness_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            batter_handedness="X",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_min_max_age_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            min_age=30,
            max_age=20,
        )
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            min_age=-5,
        )
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            max_age=-10,
        )
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            min_age=60,  # type: ignore
        )
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            max_age=70,  # type: ignore
        )


def test_fangraphs_batting_leaderboard_active_roster_only_badinput():
    with pytest.raises(ValueError):
        fg.fangraphs_batting_leaderboard(
            active_roster_only="yes",  # type: ignore
        )


def test_fangraphs_batting_leaderboard_seasons_variations():
    # valid single season
    df = fg.fangraphs_batting_leaderboard(
        start_season=2025,
        end_season=None,
    )
    print(df)
    assert df.shape[0] == 145
    assert df.shape[1] == 321
    assert df.select(pl.col("Season").unique()).item() == 2025
    assert df.select(pl.col("Name").unique()).shape[0] == 145
    assert df.select(pl.col("Team").n_unique()).item() == 31  # 31 bc some have 2TM
    # # valid multi season
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2025,
    )
    assert df.shape[0] == 229
    assert df.shape[1] == 321
    assert df.select(pl.col("Name").n_unique()).item() == 229
    assert df.select(pl.col("Team").n_unique()).item() == 31


def test_fangraphs_batting_leaderboard_dates_variations():
    # valid date range
    df = fg.fangraphs_batting_leaderboard(
        start_date="2023-04-01",
        end_date="2023-06-30",
    )
    assert df.shape[0] == 153
    assert df.shape[1] == 318
    assert df.select(pl.col("Season").unique()).item() == 2023
    assert df.select(pl.col("Name").n_unique()).item() == 153
    assert df.select(pl.col("Team").n_unique()).item() == 30


def test_fangraphs_batting_leaderboard_stat_types_variations():
    # valid stat types
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        stat_types=[
            fg.FangraphsBattingStatType.STANDARD,
            fg.FangraphsBattingStatType.ADVANCED,
        ],
    )
    assert df.shape[0] == 134
    assert df.shape[1] == 47  # fewer columns than default which is all stat types
    assert df.select(pl.col("Season").unique()).item() == 2023
    assert df.select(pl.col("Name").n_unique()).item() == 134
    assert df.select(pl.col("Team").n_unique()).item() == 31
    with pytest.raises(AttributeError):
        # invalid stat in stat types
        fg.fangraphs_batting_leaderboard(
            start_season=2023,
            end_season=2023,
            stat_types=[
                fg.FangraphsBattingStatType.std,
                fg.FangraphsBattingStatType.advanced,
            ],
        )
    df2 = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        stat_types=[],
    )
    df3 = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
    )
    assert df2.shape == df3.shape


def test_fangraphs_batting_leaderboard_batter_handedness_variations():
    # valid batter handedness L
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        batter_handedness="L",
    )
    assert df.select(pl.col("Bats").unique()).item() == "L"
    # valid batter handedness R
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        batter_handedness="R",
    )
    assert df.select(pl.col("Bats").unique()).item() == "R"
    # valid batter handedness S
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        batter_handedness="S",
    )
    assert df.select(pl.col("Bats").unique()).item() == "B"


def test_fangraphs_leaderboard_teams_variations():
    # valid team
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        team=fg.FangraphsLeaderboardTeams.YANKEES,
    )
    assert df.select(pl.col("Team").unique()).item() == "NYY"
    assert df.shape[0] == 3


def test_fangraphs_batting_leaderboard_stat_split_variations():
    # valid stat split team
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        stat_split="team",
    )
    assert df.select(pl.col("Name").unique()).shape[0] == 30  # 30 teams in 2023
    # valid stat split league
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        stat_split="league",
    )
    assert df.shape[0] == 1  # league summary only one row
    assert (
        df.select(pl.col("Name").unique()).shape[0] == 1
    )  # league always returns single row df


def test_fangraphs_batting_leaderboard_active_roster_only_variations():
    # valid active roster only true
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        active_roster_only=True,
    )
    current_year = datetime.now().year
    assert df.select(pl.col("Season").unique()).item() == 2023
    assert df.select(pl.col("Name").n_unique()).item() < 134  # fewer than total players
    # valid active roster only false
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        active_roster_only=False,
    )
    assert df.select(pl.col("Season").unique()).item() == 2023
    assert df.select(pl.col("Name").n_unique()).item() == 134  # all players


def test_fangraphs_batting_leaderboard_age_variations():
    # valid min age only
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        min_age=30,
    )
    assert df.select(pl.col("Age").min()).item() >= 30
    # valid max age only
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        max_age=25,
    )
    assert df.select(pl.col("Age").max()).item() <= 25
    # valid min and max age
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        min_age=25,
        max_age=30,
    )
    assert df.select(pl.col("Age").min()).item() >= 25
    assert df.select(pl.col("Age").max()).item() <= 30


def test_fangraphs_batting_leaderboard_position_variations():
    # valid position C
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        position=fg.FangraphsBattingPosTypes.CATCHER,
    )
    for item in df.select(pl.col("position").unique()).to_series().to_list():
        assert "C" in item


def test_fangraphs_batting_leaderboard_season_type_variations():
    # valid season type regular
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        season_type="regular",
    )
    assert df.select(pl.col("Season").unique()).item() == 2023
    # valid season type all_postseason
    df2 = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        season_type="all_postseason",
    )
    assert df2.select(pl.col("Season").unique()).item() == 2023
    assert df2.shape[0] < df.shape[0]
    # valid season type world_series
    df3 = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        season_type="world_series",
    )
    assert df3.select(pl.col("Season").unique()).item() == 2023
    assert df3.shape[0] < df2.shape[0]
    assert df3.select(pl.col("Team").n_unique()).item() == 2


def test_fangraphs_batting_leaderboard_league_variations():
    # valid league AL
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        league="al",
    )

    assert len(df.select(pl.col("Team").unique()).to_series().to_list()) == 15


def test_fangraphs_batting_leaderboard_minpa_variations():
    # valid min_pa 100
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        min_pa=100,
    )
    assert df.select(pl.col("PA").min()).item() >= 100
    # valid min_pa "y" (qualified)
    df2 = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2023,
        min_pa="y",
    )
    assert df2.select(pl.col("PA").min()).item() >= 502  # qualified in 2023 is 502 PA


def test_fangraphs_batting_leaderboard_split_seasons_variations():
    # valid split_seasons true
    df = fg.fangraphs_batting_leaderboard(
        start_season=2023,
        end_season=2025,
        split_seasons=True,
    )
    assert df.select(pl.col("Season").n_unique()).item() == 3
