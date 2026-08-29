# Statcast Leaderboards Documentation

This module provides access to several Baseball Savant leaderboard endpoints.

## Available Functions

### Park Factor Functions

- `park_factor_dimensions_leaderboard(season, metric="distance")`
- `park_factor_yearly_leaderboard(season, bat_side="", conditions="All", rolling_years=3)`
- `park_factor_distance_leaderboard(season)`

### General Functions

- `timer_infractions_leaderboard(season, perspective="Pit", min_pitches=1)`
- `abs_challenges_leaderboard(season, challenge_type="batter", game_type="regular", challenging_teams=None, opposing_teams=None, pitch_types=None, attack_zone=None, in_zone=None, min_challenges=0, min_opp_challenges=0)`
- `arm_strength_leaderboard(stat_type="player", year=2025, min_throws=50, pos="All", team=None)`
- `catcher_blocking_leaderboard(start_season, end_season, game_type="Regular", group_by="Cat", min_pitches="q", team="All", split_years=False)`
- `catcher_framing_leaderboard(start_season, end_season, group_by="catcher", game_type="Regular", min_pitches="q", teams=None, batter_handedness="ALL", pitcher_handedness="ALL", in_zone=None, min_results=1)`
- `catcher_pop_time_leaderboard(season=2026, team=None, min_2b_attempts=5, min_3b_attempts=0)`
- `catcher_stance_leaderboard(start_season, end_season, group_by="catcher", game_type="Regular", min_pitches="q", teams=None, batter_handedness="ALL", pitcher_handedness="ALL", knee_position="ALL", min_results=1, start_date=None, end_date=None)`
- `catcher_throwing_leaderboard(start_season, end_season, game_type="Regular", group_by="Cat", min_sb_attempts="q", target_base="All", team="All", split_years=False, with_team_only=True)`

### Pitcher Specific Functions

- `spin_direction_leaderboard(season="ALL", team=None, pitch_type="ALL", pitcher_handedness="ALL", min_pitches="q")`
- `active_spin_leaderboard(season, min_pitches=100, stat_method="spin-based", pitcher_handedness="ALL")`
- `arm_angle_leaderboard(start_date="2020-01-01", end_date=today, teams=None, season_type=None, pitcher_handedness="ALL", batter_handedness="ALL", pitch_types=None, min_pitches="q", group_by=None, min_group_size=1)`
- `pitch_arsenals_leaderboard(season=2026, metric_type="avg_speed", pitcher_handedness="ALL", min_pitches="q")`
- `pitch_movement_leaderboard(season=2026, pitch_type="ALL", pitcher_handedness="ALL", min_pitches="q")`
- `pitcher_running_game_leaderboard(start_season, end_season, game_type="All", group_by="Pit", pitcher_handedness="ALL", runner_movement="All", target_base="All", num_prior_disengagements="All", min_sb_opportunities="q", team="All", split_years=False)`

### Running Functions

- `baserunning_run_value_leaderboard(start_season, end_season, game_type="Regular", group_by="Runners", min_opportunities="q", team="All", split_years=False)`
- `basestealing_run_value_leaderboard(start_season, end_season, game_type="Regular", group_by="Runners", pitcher_handedness="ALL", runner_movement="All", target_base="All", num_prior_disengagements="All", min_sb_opportunities="q", team="All", split_years=False)`
- `extra_bases_taken_run_value_leaderboard(start_season, end_season, game_type="Regular", group_by="Runners", situation="all", min_opportunities="q", team="All", split_years=False)`
- `sprint_speed_leaderboard(start_season, end_season, group_by="Player", position="Position Players", min_opportunities=10, team="All", split_years=False)`
- `running_splits_leaderboard(season, position="All", team="All", bat_side="All", min_opportunities=5, split_type="Raw Split Times")`

## Function Parameters

### `park_factor_dimensions_leaderboard`

- `season` (int): Season year.
- `metric` (`"distance" | "height"`): Which fence metric set to return.

Validation:

- `season` must be between `2015` and the current in-season year.
- `metric` must be `"distance"` or `"height"`.

### `park_factor_yearly_leaderboard`

- `season` (int): Season year.
- `bat_side` (`"L" | "R" | ""`): Batter-side filter.
- `conditions` (`"All" | "Day" | "Night" | "Open Air" | "Roof Closed"`): Game-condition filter.
- `rolling_years` (int): 1, 2, or 3-year rolling window.

Validation:

- `season` must be between `1999` and the current in-season year.
- `rolling_years` must be one of `1`, `2`, `3`.

### `park_factor_distance_leaderboard`

- `season` (int): Season year.

Validation:

- `season` must be between `2016` and the current in-season year.

### `timer_infractions_leaderboard`

- `season` (int): Season year.
- `perspective` (`"Pit" | "Bat" | "Cat" | "Team"`): Perspective for leaderboard rows.
- `min_pitches` (int): Minimum pitch count threshold.

Validation:

- `season` must be between `2023` and the current in-season year.
- `min_pitches` must be at least `1`.

### `abs_challenges_leaderboard`

- `season` (int): Season year (`2025+`).
- `challenge_type` (`"batter" | "batting-team" | "catcher" | "pitcher" | "catching-team" | "team-summary" | "league"`): Grouping mode.
- `game_type` (`"regular" | "spring" | "playoff"`): Game-type filter.
- `challenging_teams` (`list[StatcastLeaderboardsTeams] | None`): Optional challenging-team filter.
- `opposing_teams` (`list[StatcastLeaderboardsTeams] | None`): Optional opposing-team filter.
- `pitch_types` (`list[...] | None`): Optional pitch-type filter (`FF`, `SI`, `FC`, `CH`, `FS`, `FO`, `SC`, `CU`, `SL`, `ST`, `SV`, `KN`).
- `attack_zone` (`list[...] | None`): Optional attack-zone filter (`11`, `12`, `13`, `14`, `16`, `17`, `18`, `19`).
- `in_zone` (`bool | None`): `True` for in-zone, `False` for out-of-zone, `None` for no filter.
- `min_challenges` (int): Minimum challenge count (`>= 0`).
- `min_opp_challenges` (int): Minimum opponent challenge count (`>= 0`).

Validation:

- `season` must be `2025` or later.
- Team filters must be lists of `StatcastLeaderboardsTeams` values or `None`.
- `min_challenges` and `min_opp_challenges` must be non-negative integers.

### `arm_strength_leaderboard`

- `stat_type` (`"player" | "team"`): Output granularity.
- `year` (int | `"All"`): `2020`..current year, or `"All"`.
- `min_throws` (int): Minimum throws threshold.
- `pos` (`"All" | "2b_ss_3b" | "outfield" | "1b" | "2b" | "3b" | "shortstop" | "lf" | "cf" | "rf"`): Position filter.
- `team` (`StatcastLeaderboardsTeams | None`): Optional team filter.

Validation:

- `min_throws` must be at least `1`.
- `team` must be `None` or a `StatcastLeaderboardsTeams` enum value.

## Catcher-Blocking Leaderboard

### `catcher_blocking_leaderboard`

This function returns the table data from Baseball Savant's Catcher Blocking
leaderboard.

- `start_season` (`int`): First season. Valid from `2018` through the current year.
- `end_season` (`int`): Last season. Must be at least `start_season`.
- `game_type` (`"Regular" | "Playoff" | "All"`): Regular season, playoffs, or both.
- `group_by` (`"Cat" | "Pit" | "Catching Team" | "League"`): Catchers, pitchers,
  catching-team aggregates, or league aggregates.
- `min_pitches` (`int | "q"`): Minimum pitches, or `"q"` for qualified players.
- `team` (`StatcastLeaderboardsTeams | "All" | "All-Split"`): Team filter.
- `split_years` (`bool`): Return separate rows by season when `True`.

When `group_by="Catching Team"`, Baseball Savant ignores the team and minimum-pitch
filters. The function follows this behavior.

Validation:

- `start_season` and `end_season` must be valid seasons from 2018 through the current year.
- `end_season` must not precede `start_season`.
- `min_pitches` must be a positive integer or `"q"`.
- `team` must be a supported team enum, `"All"`, or `"All-Split"`.

## Catcher-Framing Leaderboard

### `catcher_framing_leaderboard`

This function returns Baseball Savant's Catcher Framing leaderboard table.

- `start_season` (`int`): First season. Valid from `2018` through the current year.
- `end_season` (`int`): Last season. Must be at least `start_season`.
- `group_by` (`"catcher" | "catching-team" | "batter" | "batting-team" | "pitcher" | "league"`):
  Entity type for the returned rows.
- `game_type` (`"Any" | "Regular" | "Playoff"`): Game-type filter.
- `min_pitches` (`int | "q"`): Minimum shadow pitches, or `"q"` for qualified players.
- `teams` (`list[StatcastLeaderboardsTeams] | None`): Teams to include. `None` includes all teams.
- `batter_handedness` (`"L" | "R" | "ALL"`): Batter-side filter.
- `pitcher_handedness` (`"L" | "R" | "ALL"`): Pitcher-hand filter.
- `in_zone` (`bool | None`): `True` for in-zone pitches, `False` for out-of-zone pitches,
  or `None` for both.
- `min_results` (`int`): Minimum number of results. Must be at least `1`.

Validation:

- `start_season` and `end_season` must be valid seasons from `2018` through the current year.
- `end_season` must not precede `start_season`.
- `min_pitches` must be a positive integer or `"q"`.
- `teams` must be a list of `StatcastLeaderboardsTeams` values or `None`.
- `min_results` must be at least `1`.

## Catcher Pop Time Leaderboard

### `catcher_pop_time_leaderboard`

This function returns Baseball Savant's Catcher Pop Time leaderboard table.

- `season` (`int`): Season from `2015` through the current year.
- `team` (`StatcastLeaderboardsTeams | None`): Optional team filter.
- `min_2b_attempts` (`int`): Minimum second-base attempts.
- `min_3b_attempts` (`int`): Minimum third-base attempts.

Validation:

- `season` must be between `2015` and the current year.
- `team` must be `None` or a `StatcastLeaderboardsTeams` enum value.
- `min_2b_attempts` and `min_3b_attempts` must be integers.

## Catcher Stance Leaderboard

### `catcher_stance_leaderboard`

This function returns Baseball Savant's Catcher Stance leaderboard table.

- `start_season` (`int`): First season. Valid from `2020` through the current year.
- `end_season` (`int`): Last season. Must be at least `start_season`.
- `group_by` (`"catcher" | "catching-team" | "batter" | "batting-team" | "pitcher" | "league"`):
  Entity type for the returned rows.
- `game_type` (`"Any" | "Regular" | "Playoff"`): Game-type filter.
- `min_pitches` (`int | "q"`): Minimum pitch threshold, or `"q"` for qualified players.
- `teams` (`list[StatcastLeaderboardsTeams] | None`): Teams to include. `None` includes all teams.
- `batter_handedness` (`"L" | "R" | "ALL"`): Batter-side filter.
- `pitcher_handedness` (`"L" | "R" | "ALL"`): Pitcher-hand filter.
- `knee_position` (`"ALL" | "Knee(s) Down" | "Both Up" | "Both Down" | "R Up, L Down" | "L Up, R Down"`):
  Catcher stance filter.
- `min_results` (`int`): Minimum number of results. Must be at least `1`.
- `start_date` (`str | None`): Optional start date in `YYYY-MM-DD` format.
- `end_date` (`str | None`): Optional end date in `YYYY-MM-DD` format.

Validation:

- `start_season` and `end_season` must be valid seasons from `2020` through the current year.
- `end_season` must not precede `start_season`.
- `min_pitches` must be a positive integer or `"q"`.
- `teams` must be a list of `StatcastLeaderboardsTeams` values or `None`.
- `min_results` must be at least `1`.
- Dates must be from `2020-07-23` through today, and `end_date` must not precede `start_date`.

## Catcher Throwing Leaderboard

### `catcher_throwing_leaderboard`

This function returns Baseball Savant's Catcher Throwing leaderboard table.

- `start_season` (`int`): First season. Valid from `2016` through the current year.
- `end_season` (`int`): Last season. Must be at least `start_season`.
- `game_type` (`"Regular" | "Playoff" | "All"`): Game-type filter.
- `group_by` (`"Cat" | "Pitching Team" | "League"`): Catchers, catching-team aggregates, or league aggregates.
- `min_sb_attempts` (`int | "q"`): Minimum stolen-base attempt threshold, or `"q"` for qualified players.
- `target_base` (`"2B" | "3B" | "All"`): Base targeted by the throw.
- `team` (`StatcastLeaderboardsTeams | "All" | "All-Split"`): Team filter.
- `split_years` (`bool`): Return separate rows by season when `True`.
- `with_team_only` (`bool`): Include only rows with a team when `True`.

Validation:

- `start_season` and `end_season` must be valid seasons from `2016` through the current year.
- `end_season` must not precede `start_season`.
- `min_sb_attempts` must be a positive integer or `"q"`.
- `team` must be a supported team enum, `"All"`, or `"All-Split"`.
- `split_years` and `with_team_only` must be booleans.

## Pitcher Leaderboards

### `spin_direction_leaderboard`

- `season` (int | `"ALL"`): Season year between `2020` and current year, or `"ALL"` for all available years.
- `team` (`StatcastLeaderboardsTeams | None`): Optional team filter.
- `pitch_type` (`"FF" | "SI" | "FC" | "CH" | "FS" | "FO" | "SC" | "CU" | "SL" | "ST" | "SV" | "KN" | "ALL"`): Pitch type filter.
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher handedness filter.
- `min_pitches` (int | `"q"`): Minimum pitch count threshold or qualifying threshold.

Validation:

- `season` must be between `2020` and current year, or `"ALL"`.
- `pitch_type` must be a valid pitch type or `"ALL"`.
- `pitcher_handedness` must be `"R"`, `"L"`, or `"ALL"`.
- `min_pitches` must be a positive integer or `"q"`.
- `team` must be `None` or a `StatcastLeaderboardsTeams` enum value.

### `active_spin_leaderboard`

- `season` (int): Season year between `2017` and current year.
- `min_pitches` (int): Minimum pitch count threshold. Defaults to `100`.
- `stat_method` (`"spin-based" | "observed"`): Calculation method for active spin. `"spin-based"` available from 2020+, `"observed"` from 2017+.
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher handedness filter.

Validation:

- `season` must be between `2017` and current year.
- `min_pitches` must be at least `1`.
- `stat_method` must be `"spin-based"` or `"observed"`.
- If `stat_method` is `"spin-based"`, `season` must be `2020` or later.
- `pitcher_handedness` must be `"R"`, `"L"`, or `"ALL"`.

### `arm_angle_leaderboard`

- `start_date` (str): Start date in `YYYY-MM-DD` format. Earliest possible: `2020-01-01`.
- `end_date` (str): End date in `YYYY-MM-DD` format. Must be after `start_date` and cannot be in future.
- `teams` (`list[StatcastLeaderboardsTeams] | None`): Optional list of teams to filter.
- `season_type` (`list[...] | None`): Optional season types: `"R"` (Regular), `"WC"` (Wild Card), `"DS"` (Divisional Series), `"CS"` (Championship Series), `"WS"` (World Series).
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher handedness filter.
- `batter_handedness` (`"R" | "L" | "ALL"`): Batter handedness filter.
- `pitch_types` (`list[...] | None`): Optional list of pitch types to filter.
- `min_pitches` (int | `"q"`): Minimum pitch count threshold or qualifying threshold.
- `group_by` (`list[...] | None`): Optional grouping dimensions (max 4). Options: `"season"`, `"month"`, `"pitch_type"`, `"game_type"`, `"bat_side"`, `"fielding_team"`.
- `min_group_size` (int): Minimum group size threshold. Defaults to `1`.

Validation:

- Date format must be `YYYY-MM-DD`.
- `end_date` must be after `start_date` and not in the future.
- All list parameters must contain valid values or be `None`.
- `min_pitches` must be a positive integer or `"q"`.
- `group_by` cannot have more than 4 items.
- `min_group_size` must be at least `1`.

### `pitch_arsenals_leaderboard`

- `season` (int): Season year between `2008` and current year. Defaults to `2026`.
- `metric_type` (`"avg_speed" | "usage_percentage" | "avg_spin"`): Metric to retrieve. Defaults to `"avg_speed"`.
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher handedness filter.
- `min_pitches` (int | `"q"`): Minimum pitch count threshold or qualifying threshold.

Validation:

- `season` must be between `2008` and current year.
- `metric_type` must be one of the valid options.
- `pitcher_handedness` must be `"R"`, `"L"`, or `"ALL"`.
- `min_pitches` must be a positive integer or `"q"`.

### `pitch_movement_leaderboard`

- `season` (int): Season year between `2017` and current year. Defaults to `2026`.
- `pitch_type` (`"FF" | "SI" | "FC" | "CH" | "FS" | "FO" | "SC" | "CU" | "SL" | "ST" | "SV" | "KN" | "ALL"`): Pitch type filter.
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher handedness filter.
- `min_pitches` (int | `"q"`): Minimum pitch count threshold or qualifying threshold.

Validation:

- `season` must be between `2017` and current year.
- `pitch_type` must be a valid pitch type or `"ALL"`.
- `pitcher_handedness` must be `"R"`, `"L"`, or `"ALL"`.
- `min_pitches` must be a positive integer or `"q"`.

### `pitcher_running_game_leaderboard`

- `start_season` (int): Starting season year. Must be `2016` or later.
- `end_season` (int): Ending season year. Must be >= `start_season`.
- `game_type` (`"Regular" | "Playoff" | "All"`): Game type filter. Defaults to `"All"`.
- `group_by` (`"Pit" | "Pitching Team" | "League"`): Aggregation level. Defaults to `"Pit"`.
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher handedness filter.
- `runner_movement` (`"All" | "Advance" | "Out" | "Hold"`): Filter by runner outcome.
- `target_base` (`"All" | "2B" | "3B"`): Base being targeted.
- `num_prior_disengagements` (`"All" | "0" | "1" | "2" | "3+"`): Number of prior pitcher disengagements.
- `min_sb_opportunities` (int | `"q"`): Minimum stolen base opportunity count.
- `team` (`StatcastLeaderboardsTeams | "All" | "All-Split"`): Team filter. `"All"` for all teams, `"All-Split"` to split by each team.
- `split_years` (bool): Whether to split results by individual season. Defaults to `False`.

Validation:

- `start_season` must be between `2016` and current year.
- `end_season` must be between `start_season` and current year.
- All `Literal` parameters must be valid options.
- `min_sb_opportunities` must be a positive integer or `"q"`.

### `baserunning_run_value_leaderboard`

This function returns Baseball Savant's Baserunning Run Value leaderboard table.

- `start_season` (int): First season. Valid from `2016` through the current year.
- `end_season` (int): Last season. Must be at least `start_season`.
- `game_type` (`"Regular" | "Playoff" | "All"`): Regular season, playoffs, or both.
- `group_by` (`"Runners" | "Running Team" | "Pitching Team" | "League"`):
  Entity type for the returned rows. `"Runners"` returns individual runners,
  `"Running Team"` returns running-team aggregates, `"Pitching Team"` returns
  pitching-team aggregates, and `"League"` returns league aggregates.
- `min_opportunities` (int | `"q"`): Minimum baserunning opportunities, or `"q"`
  for Baseball Savant's qualifying threshold.
- `team` (`StatcastLeaderboardsTeams | "All" | "All-Split"`): Team filter.
  `"All"` includes all teams, and `"All-Split"` returns separate team stints.
- `split_years` (bool): Return one row per season when `True`; otherwise aggregate
  across the requested season range.

Validation:

- `start_season` and `end_season` must be valid seasons from `2016` through the current year.
- `end_season` must not precede `start_season`.
- `game_type` and `group_by` must be one of the listed values.
- `min_opportunities` must be a positive integer or `"q"`.
- `team` must be a supported team enum, `"All"`, or `"All-Split"`.
- `split_years` must be a boolean.

Runner results use `player_id` and `player_name`. Team results use `team_id`,
`team_name`, and `team_abbr`; league results use `league_id` and `league_name`.

### `basestealing_run_value_leaderboard`

This function returns Baseball Savant's Basestealing Run Value leaderboard table.

- `start_season` (int): First season. Valid from `2016` through the current year.
- `end_season` (int): Last season. Must be at least `start_season`.
- `game_type` (`"Regular" | "Playoff" | "All"`): Regular season, playoffs, or both.
- `group_by` (`"Runners" | "Running Team" | "League"`): Entity type for the
  returned rows.
- `pitcher_handedness` (`"R" | "L" | "ALL"`): Pitcher-hand filter.
- `runner_movement` (`"All" | "Advance" | "Out" | "Hold"`): Runner-outcome filter.
- `target_base` (`"All" | "2B" | "3B"`): Target-base filter.
- `num_prior_disengagements` (`"All" | "0" | "1" | "2" | "3+"`): Number of prior
  pitcher disengagements. `"3+"` includes three or more.
- `min_sb_opportunities` (int | `"q"`): Minimum stolen-base opportunity count, or
  `"q"` for Baseball Savant's qualifying threshold.
- `team` (`StatcastLeaderboardsTeams | "All" | "All-Split"`): Team filter.
  `"All"` includes all teams, and `"All-Split"` returns separate team stints.
- `split_years` (bool): Return one row per season when `True`; otherwise aggregate
  across the requested season range.

Validation:

- `start_season` and `end_season` must be valid seasons from `2016` through the current year.
- `end_season` must not precede `start_season`.
- All enum parameters must use one of the listed values.
- `min_sb_opportunities` must be a positive integer or `"q"`.
- `team` must be a supported team enum, `"All"`, or `"All-Split"`.
- `split_years` must be a boolean.

The returned CSV already uses `player_id`, `player_name`, and `team_name` for
runner, team, and league groupings.

### `extra_bases_taken_run_value_leaderboard`

This function returns Baseball Savant's Extra Bases Taken Run Value leaderboard.

- `start_season` (int): First season. Valid from `2016` through the current year.
- `end_season` (int): Last season. Must be at least `start_season`.
- `game_type` (`"Regular" | "Playoff" | "All"`): Regular season, playoffs, or both.
- `group_by` (`"Runners" | "Fielders" | "Pitchers" | "Batting Team" | "Fielding Team" | "League"`): Entity type for the returned rows.
- `situation` (str): Short base/out situation key. Accepted values are:
  `"all"` (all situations), `"batter_1b_to_2b"` (batter from first to second),
  `"batter_2b_to_3b"` (batter from second to third),
  `"runner_1b_to_3b_lt_2_outs"` (runner from first to third with fewer than two outs),
  `"runner_1b_to_3b_2_outs"` (runner from first to third with two outs),
  `"runner_1b_to_home_lt_2_outs"` (runner from first to home with fewer than two outs),
  `"runner_1b_to_home_2_outs"` (runner from first to home with two outs),
  `"runner_2b_to_home_lt_2_outs"` (runner from second to home with fewer than two outs),
  `"runner_2b_to_home_2_outs"` (runner from second to home with two outs),
  `"runner_3b_to_home_first_out"` (runner from third to home on the first out),
  and `"runner_3b_to_home_second_out"` (runner from third to home on the second out).
- `min_opportunities` (int | `"q"`): Minimum advance-opportunity count, or `"q"` for Baseball Savant's qualifying threshold.
- `team` (`StatcastLeaderboardsTeams | "All" | "All-Split"`): Team filter. `"All"` includes all teams, and `"All-Split"` returns separate team stints.
- `split_years` (bool): Return one row per season when `True`; otherwise aggregate across the requested season range.

Validation:

- `start_season` and `end_season` must be valid seasons from `2016` through the current year.
- `end_season` must not precede `start_season`.
- `game_type`, `group_by`, and `situation` must use one of the listed values.
- `min_opportunities` must be a positive integer or `"q"`.
- `team` must be a supported team enum, `"All"`, or `"All-Split"`.
- `split_years` must be a boolean.

Player results use `player_id` and `player_name`. Team results use `team_id`,
`team_name`, and `team_abbr`; league results use `league_id` and `league_name`.

`StatcastLeaderboardsTeams.show_options()` returns all supported team options.

### `sprint_speed_leaderboard`

This function returns Baseball Savant's Sprint Speed leaderboard.

- `start_season` (int): First season. Valid from `2015` through the current year.
- `end_season` (int): Last season. Must be at least `start_season`.
- `group_by` (`"Player" | "Team"`): Row type. Player results support a season range. Team results support one season or the split-years view.
- `position` (`"Position Players" | "All" | "C" | "1B" | "2B" | "SS" | "3B" | "LF" | "CF" | "RF" | "DH" | "P"`): Player-position filter. `"Position Players"` excludes pitchers; `"All"` includes pitchers. Used only for player results.
- `min_opportunities` (int): Minimum competitive-run count. Must be non-negative. Used only for player results.
- `team` (`StatcastLeaderboardsTeams | "All"`): Team filter.
- `split_years` (bool): For team results, use Baseball Savant's `"All - Split Years"` view when `True`. Player results ignore this parameter.

Validation:

- `start_season` and `end_season` must be valid seasons from `2015` through the current year.
- `end_season` must not precede `start_season`.
- `group_by` and `position` must use one of the listed values.
- `min_opportunities` must be a non-negative integer.
- Team results require matching seasons unless `split_years=True`.
- `team` must be a supported team enum or `"All"`.
- `split_years` must be a boolean.

Player results use `player_id`, `player_name`, and `team_abbr`. Team results use
`team_id` and `team_name`.

### `running_splits_leaderboard`

This function returns Baseball Savant's 90ft Running Splits leaderboard.

- `season` (int): Season year. Valid from `2015` through the current year.
- `position` (`"All" | "C" | "1B" | "2B" | "SS" | "3B" | "LF" | "CF" | "RF" | "DH"`): Position filter.
- `team` (`StatcastLeaderboardsTeams | "All"`): Team filter.
- `bat_side` (`"All" | "Right" | "Left"`): Batter-side filter.
- `min_opportunities` (int): Minimum running-split opportunities. Must be a positive integer.
- `split_type` (`"Raw Split Times" | "Percentile Rankings"`): Output format for the split-time columns.

Validation:

- `season` must be between `2015` and the current year.
- `position`, `bat_side`, and `split_type` must use one of the listed values.
- `min_opportunities` must be a positive integer.
- `team` must be a supported team enum or `"All"`.

Player comparison selectors on the Baseball Savant page affect only the
visualization and are not included in this function.

Results use `player_id`, `player_name`, `team_abbr`, and `position`.

```python
import pybaseballstats.statcast_leaderboards as sl
print(sl.StatcastLeaderboardsTeams.show_options())
```

## Example Usage

### Park dimensions leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.park_factor_dimensions_leaderboard(season=2025, metric="distance")
print(df)
```

### 90ft Running Splits leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.running_splits_leaderboard(
    season=2023,
    position="SS",
    bat_side="Right",
    min_opportunities=5,
    split_type="Raw Split Times",
)
print(df)
```

### Park yearly leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.park_factor_yearly_leaderboard(
    season=2025,
    bat_side="L",
    conditions="All",
    rolling_years=3,
)
print(df)
```

### Park factor distance leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.park_factor_distance_leaderboard(season=2025)
print(df)
```

### Pitch timer infractions leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.timer_infractions_leaderboard(
    season=2025,
    perspective="Pit",
    min_pitches=50,
)
print(df)
```

### Arm strength leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.arm_strength_leaderboard(
    stat_type="player",
    year=2025,
    min_throws=100,
    pos="rf",
    team=sl.StatcastLeaderboardsTeams.YANKEES,
)
print(df)
```

### ABS challenges leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.abs_challenges_leaderboard(
    season=2025,
    challenge_type="batter",
    game_type="regular",
    challenging_teams=[sl.StatcastLeaderboardsTeams.YANKEES],
    opposing_teams=[sl.StatcastLeaderboardsTeams.RED_SOX],
    pitch_types=["FF", "SL"],
    attack_zone=["11", "19"],
    in_zone=True,
    min_challenges=5,
    min_opp_challenges=2,
)
print(df)
```

### Catcher framing leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.catcher_framing_leaderboard(
    start_season=2024,
    end_season=2024,
    group_by="catcher",
    game_type="Regular",
    min_pitches=100,
    teams=[sl.StatcastLeaderboardsTeams.BLUE_JAYS],
    batter_handedness="L",
    pitcher_handedness="R",
    in_zone=True,
    min_results=25,
)
print(df)
```

### Catcher Pop Time leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.catcher_pop_time_leaderboard(
    season=2025,
    team=sl.StatcastLeaderboardsTeams.BLUE_JAYS,
    min_2b_attempts=10,
    min_3b_attempts=5,
)
print(df)
```

### Catcher Stance leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.catcher_stance_leaderboard(
    start_season=2023,
    end_season=2023,
    group_by="catcher",
    game_type="Regular",
    min_pitches=100,
    teams=[sl.StatcastLeaderboardsTeams.BLUE_JAYS],
    batter_handedness="L",
    pitcher_handedness="R",
    knee_position="Knee(s) Down",
    min_results=25,
    start_date="2023-04-01",
    end_date="2023-10-01",
)
print(df)
```

### Catcher Throwing leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.catcher_throwing_leaderboard(
    start_season=2023,
    end_season=2023,
    game_type="Regular",
    group_by="Cat",
    min_sb_attempts=10,
    target_base="2B",
    team=sl.StatcastLeaderboardsTeams.BLUE_JAYS,
    split_years=False,
    with_team_only=True,
)
print(df)
```

### Spin direction leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

# Get spin direction data for all seasons, all pitch types
df = sl.spin_direction_leaderboard(season="ALL", pitch_type="ALL")
print(df)

# Get 2024 fastball spin direction by right-handed pitchers
df = sl.spin_direction_leaderboard(
    season=2024,
    pitch_type="FF",
    pitcher_handedness="R",
    min_pitches=50,
)
print(df)
```

### Active spin leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

# Get observed active spin data for 2024
df = sl.active_spin_leaderboard(
    season=2024,
    stat_method="observed",
    min_pitches=100,
)
print(df)

# Get spin-based active spin (2020+) for right-handed pitchers
df = sl.active_spin_leaderboard(
    season=2024,
    stat_method="spin-based",
    pitcher_handedness="R",
    min_pitches=100,
)
print(df)
```

### Arm angle leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

# Get arm angle data for 2024 regular season
df = sl.arm_angle_leaderboard(
    start_date="2024-03-28",
    end_date="2024-09-30",
    season_type=["R"],  # Regular season only
    pitcher_handedness="L",  # Left-handed pitchers
    min_pitches=100,
)
print(df)

# Get arm angle grouped by month and pitch type
df = sl.arm_angle_leaderboard(
    start_date="2024-01-01",
    end_date="2024-12-31",
    group_by=["month", "pitch_type"],
    min_group_size=10,
)
print(df)

# Get arm angle for specific team(s)
df = sl.arm_angle_leaderboard(
    start_date="2024-03-28",
    end_date="2024-09-30",
    teams=[sl.StatcastLeaderboardsTeams.YANKEES, sl.StatcastLeaderboardsTeams.RED_SOX],
)
print(df)
```

### Pitch arsenals leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

# Get average fastball velocity for 2024
df = sl.pitch_arsenals_leaderboard(
    season=2024,
    metric_type="avg_speed",
    pitcher_handedness="ALL",
)
print(df)

# Get pitch usage percentages
df = sl.pitch_arsenals_leaderboard(
    season=2024,
    metric_type="usage_percentage",
    pitcher_handedness="R",
)
print(df)

# Get average spin rate for left-handed pitchers
df = sl.pitch_arsenals_leaderboard(
    season=2024,
    metric_type="avg_spin",
    pitcher_handedness="L",
    min_pitches=100,
)
print(df)
```

### Pitch movement leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

# Get movement data for 4-seam fastballs in 2024
df = sl.pitch_movement_leaderboard(
    season=2024,
    pitch_type="FF",
    pitcher_handedness="ALL",
    min_pitches=100,
)
print(df)

# Get slider movement for right-handed pitchers
df = sl.pitch_movement_leaderboard(
    season=2024,
    pitch_type="SL",
    pitcher_handedness="R",
    min_pitches="q",  # Qualifying threshold
)
print(df)
```

### Pitcher running game leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

# Get pitcher stolen base prevention for 2023-2024
df = sl.pitcher_running_game_leaderboard(
    start_season=2023,
    end_season=2024,
    game_type="Regular",
    group_by="Pit",  # Individual pitcher results
    min_sb_opportunities=10,
)
print(df)

# Get results split by team (for players who played for multiple teams)
df = sl.pitcher_running_game_leaderboard(
    start_season=2024,
    end_season=2024,
    team="All-Split",
    split_years=False,  # Aggregate across the season
    min_sb_opportunities=5,
)
print(df)

# Get results aggregated by pitching team
df = sl.pitcher_running_game_leaderboard(
    start_season=2024,
    end_season=2024,
    group_by="Pitching Team",
    runner_movement="Advance",  # Only runners who advanced
    target_base="2B",  # Only 2nd base steal attempts
)
print(df)

# Get pitcher running game data by left-handed pitchers, split by season
df = sl.pitcher_running_game_leaderboard(
    start_season=2022,
    end_season=2024,
    pitcher_handedness="L",
    split_years=True,  # Separate row for each year
    min_sb_opportunities="q",
)
print(df)
```

### Baserunning Run Value leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.baserunning_run_value_leaderboard(
    start_season=2023,
    end_season=2024,
    game_type="Regular",
    group_by="Runners",
    min_opportunities=10,
    team="All",
    split_years=True,
)
print(df)
```

### Basestealing Run Value leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.basestealing_run_value_leaderboard(
    start_season=2023,
    end_season=2024,
    game_type="Regular",
    group_by="Runners",
    pitcher_handedness="ALL",
    runner_movement="All",
    target_base="All",
    num_prior_disengagements="All",
    min_sb_opportunities=10,
    team="All",
    split_years=True,
)
print(df)
```

### Extra Bases Taken Run Value leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.extra_bases_taken_run_value_leaderboard(
    start_season=2023,
    end_season=2024,
    group_by="Runners",
    situation="all",
    min_opportunities=10,
    team="All",
    split_years=True,
)
print(df)
```

### Sprint Speed leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.sprint_speed_leaderboard(
    start_season=2023,
    end_season=2024,
    group_by="Player",
    position="CF",
    min_opportunities=10,
    team="All",
)
print(df)
```

1. Some leaderboard functions use Playwright to render and parse table HTML, which can be slower than pure CSV/API endpoints.
2. Returned data is always a Polars DataFrame.
3. Column names can differ by endpoint because they mirror Baseball Savant output and then apply endpoint-specific renaming.
