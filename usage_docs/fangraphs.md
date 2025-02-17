# Fangraphs Usage Docs

## Data Source

Fangraphs functionality is based of of their leaderboard search feature which can be found [here](https://www.fangraphs.com/leaders/major-league)

## Available Functions

1. fangraphs_batting_range
    - Options:
      - start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
      - end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
      - start_season (str, optional): The start season for the range. Defaults to None.
      - end_season (str, optional): The end season for the range. Defaults to None.
      - stat_types (List[FangraphsBattingStatType], optional): List of stat types to fetch. Defaults to None.
      - return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
      - pos (FangraphsBattingPosTypes, optional): The position type to filter by. Defaults to FangraphsBattingPosTypes.ALL.
      - league (FangraphsLeagueTypes, optional): The league type to filter by. Defaults to FangraphsLeagueTypes.ALL.
      - qual (str, optional): Minimum at-bats qualifier. Defaults to "y".
      - handedness (str, optional): The handedness of the batter ('', 'R', 'L', 'S'). Defaults to "".
      - rost (int, optional): Roster status (0 for all players, 1 for active roster). Defaults to 0.
      - team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
      - stat_split (FangraphsStatSplitTypes, optional): The stat split type. Defaults to FangraphsStatSplitTypes.PLAYER.
2. fangraphs_pitching_range
    - Options:
      - start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
      - end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
      - start_season (str, optional): The start season for the range in 'YYYY' format. Defaults to None.
      - end_season (str, optional): The end season for the range in 'YYYY' format. Defaults to None.
      - stat_types (List[FangraphsPitchingStatType], optional): List of pitching stat types to retrieve. Defaults to None.
      - starter_reliever (str, optional): Filter for starters, relievers, or all. Defaults to "all".
      - return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
      - league (FangraphsLeagueTypes, optional): The league to filter by. Defaults to FangraphsLeagueTypes.ALL.
      - team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
      - qual (str, optional): Qualification status. Defaults to "y".
      - rost (int, optional): Roster status, 0 for all players, 1 for active roster. Defaults to 0.
      - handedness (str, optional): Filter by handedness (e.g., 'R' for right-handed, 'L' for left-handed). Defaults to "".
      - stat_split (FangraphsStatSplitTypes, optional): The type of stat split to apply. Defaults to FangraphsStatSplitTypes.PLAYER.
3. fangraphs_fielding_range
    - Options:
      - start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
      - end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
      - start_season (str, optional): The start season year. Defaults to None.
      - end_season (str, optional): The end season year. Defaults to None.
      - stat_types (List[FangraphsPitchingStatType], optional): List of pitching stat types to retrieve. Defaults to None.
      - return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
      - league (FangraphsLeagueTypes, optional): The league type to filter by. Defaults to FangraphsLeagueTypes.ALL.
      - team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
      - qual (str, optional): The qualification type. Defaults to "y".
      - rost (int, optional): Roster status, 0 for all players, 1 for active roster. Defaults to 0.
      - pos (FangraphsBattingPosTypes, optional): The batting position type to filter by. Defaults to FangraphsBattingPosTypes.ALL.
      - stat_split (FangraphsStatSplitTypes, optional): The stat split type. Defaults to FangraphsStatSplitTypes.PLAYER.
