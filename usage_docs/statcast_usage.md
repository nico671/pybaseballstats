# Statcast Usage Docs

## Data Source

Data is pulled from the MLB's Statcast API, which is powered by Baseball Savant. The API I am providing is modeled on the search functionality provided at [Baseball Savant](https://baseballsavant.mlb.com/statcast_search).

## Available Functions

1. `statcast_date_range`
   - Options
      - `start_date`
        - str: 'YYYY-MM-DD'
      - `end_date`
          - str: 'YYYY-MM-DD'
      - `team`
          - str: 'team abbreviation' (e.g. 'NYY'), the default is returning data for all teams
      - `return_pandas`
          - bool: whether or not to return a pandas DataFrame (default behavior is a Polars lazyframe)
      - `extra_stats`
          - bool: whether or not to include extra stats from Baseball Savant (default is False)
   - Examples:
      - `statcast_date_range('2021-04-01', '2021-04-30')` (returns data for all teams, as a Polars lazyframe, without extra stats)
      - `statcast_date_range('2021-04-01', '2021-04-30', team='NYY')` (returns data for the New York Yankees, as a Polars lazyframe, without extra stats)
      - `statcast_date_range('2021-04-01', '2021-04-30', return_pandas=True, extra_stats=True)` (returns data for all teams, as a pandas DataFrame, with extra stats)
2. `statcast_single_game`

   - Options
      - `game_pk`
        - int: the MLB game primary key
      - `extra_stats`
        - bool: whether or not to include extra stats from Baseball Savant (default is False)
      - `return_pandas`
        - bool: whether or not to return a pandas DataFrame (default behavior is a Polars lazyframe)

   - Examples:
     - `statcast_single_game(634, return_pandas=True, extra_stats=True)` (returns data for game 634, as a pandas DataFrame, with extra stats)
     - `statcast_single_game(634, extra_stats=True)` (returns data for game 634, as a Polars lazyframe, with extra stats)
     - `statcast_single_game(634)` (returns data for game 634, as a Polars lazyframe, without extra stats)
