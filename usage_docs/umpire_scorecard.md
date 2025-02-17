# Umpire Scorecard Usage Docs

## Data Source

## Available Functions

1. umpire_games_date_range
    - Options:
      - start_date (str): Start date in 'YYYY-MM-DD' format.
      - end_date (str): Start date in 'YYYY-MM-DD' format.
      - season_type (str, optional): Restrict games to only regular season games ("R"), only postseason games ("P") or both ("*"). Defaults to "*".
      - home_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the home team. Defaults to UmpireScorecardTeams.ALL.
      - away_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the away team. Defaults to UmpireScorecardTeams.ALL.
      - umpire_name (str, optional): Restrict games to ones where the name of the umpire matches the parameter. If "" then all umpires are allowed. Defaults to "".
      - return_pandas (bool, optional): If true return data as pandas Dataframe instead of a polars Dataframe. Defaults to False.
2. umpire_stats_date_range
    - Options:
      - start_date (str): Start date in 'YYYY-MM-DD' format.
      - end_date (str): Start date in 'YYYY-MM-DD' format.
      - season_type (str, optional): Restrict games to only regular season games ("R"), only postseason games ("P") or both ("*"). Defaults to "*".
      - home_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the home team. Defaults to UmpireScorecardTeams.ALL.
      - away_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the away team. Defaults to UmpireScorecardTeams.ALL.
      - return_pandas (bool, optional): If true return data as pandas Dataframe instead of a polars Dataframe. Defaults to False.

3. team_umpire_stats_date_range
   - Options:
     - start_date (str): Start date in 'YYYY-MM-DD' format.
     - end_date (str): Start date in 'YYYY-MM-DD' format.
     - season_type (str, optional): Restrict games to only regular season games ("R"), only postseason games ("P") or both ("*"). Defaults to "*".
     - team (UmpireScorecardTeams, optional): Restrict data to a specific team only. Defaults to UmpireScorecardTeams.ALL.
     - home_away (str, optional): Restrict data to be calculated on only home games ("h"), away games ("a") or both ("*"). Defaults to "*".
     - stadium (UmpireScorecardTeams, optional): Restrict data to be calculated on only games occuring at the given stadium. Defaults to UmpireScorecardTeams.ALL.
     - umpire_name (str, optional): Restrict data to be calculated only for a given umpire. Defaults to "".
     - return_pandas (bool, optional): If true return data as pandas Dataframe instead of a polars Dataframe. Defaults to False.
