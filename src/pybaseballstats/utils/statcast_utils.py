import asyncio
import datetime as dt
from typing import Iterator, List, Tuple

import aiohttp
import pandas as pd
import polars as pl
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

# https://github.com/jldbc/pybaseball/blob/master/pybaseball/statcast.py and  https://github.com/jldbc/pybaseball/blob/master/pybaseball/statcast_batter.py
# used for root_url, single_game, date_range
ROOT_URL = "https://baseballsavant.mlb.com"
SINGLE_GAME = "/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
DATE_RANGE = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type={pos}&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
DATE_RANGE_SINGLE_BATTER = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&&batters_lookup%5B%5D={batter_id}&player_type={pos}&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
DATE_RANGE_SINGLE_PITCHER = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&pitchers_lookup%5B%5D={pitcher_id}&player_type={pos}&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
# my own url
EXTRA_STATS = "/statcast_search/csv?hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2024%7C2023%7C2022%7C2021%7C2020%7C2019%7C2018%7C2017%7C2016%7C2015%7C2014%7C2013%7C2012%7C2011%7C2010%7C2009%7C2008%7C&hfSit=&player_type={pos}&game_date_gt=&game_date_lt=&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=is%5C.%5C.remove%5C.%5C.bunts%7Cis%5C.%5C.competitive%7C&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_whiffs=on&chk_stats_swings=on&chk_stats_api_break_z_with_gravity=on&chk_stats_api_break_x_arm=on&chk_stats_api_break_z_induced=on&chk_stats_api_break_x_batter_in=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_xobpdiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_barrels_total=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_run_exp=on&chk_stats_pitcher_run_exp=on&chk_stats_swing_miss_percent=on&chk_stats_batter_run_value_per_100=on&chk_stats_pitcher_run_value_per_100=on&chk_stats_velocity=on&chk_stats_effective_speed=on&chk_stats_spin_rate=on&chk_stats_release_pos_z=on&chk_stats_release_pos_x=on&chk_stats_release_extension=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_arm_angle=on&chk_stats_launch_speed=on&chk_stats_hyper_speed=on&chk_stats_sweetspot_speed_mph=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_swing_length=on&chk_stats_hardhit_percent=on&chk_stats_barrels_per_bbe_percent=on&chk_stats_barrels_per_pa_percent=on&chk_stats_pos3_int_start_distance=on&chk_stats_pos4_int_start_distance=on&chk_stats_pos5_int_start_distance=on&chk_stats_pos6_int_start_distance=on&chk_stats_pos7_int_start_distance=on&chk_stats_pos8_int_start_distance=on&chk_stats_pos9_int_start_distance=on#results"
YEAR_RANGES = {
    2022: (dt.date(2022, 3, 17), dt.date(2022, 11, 5)),
    2016: (dt.date(2016, 4, 3), dt.date(2016, 11, 2)),
    2019: (dt.date(2019, 3, 20), dt.date(2019, 10, 30)),
    2017: (dt.date(2017, 4, 2), dt.date(2017, 11, 1)),
    2023: (dt.date(2023, 3, 15), dt.date(2023, 11, 1)),
    2020: (dt.date(2020, 7, 23), dt.date(2020, 10, 27)),
    2018: (dt.date(2018, 3, 29), dt.date(2018, 10, 28)),
    2015: (dt.date(2015, 4, 5), dt.date(2015, 11, 1)),
    2024: (dt.date(2024, 3, 15), dt.date(2024, 10, 25)),
    2021: (dt.date(2021, 3, 15), dt.date(2021, 11, 2)),
    2025: (dt.date(2025, 3, 15), dt.date(2025, 11, 2)),
}

STATCAST_DATE_FORMAT = "%Y-%m-%d"


async def _fetch_data(session, url, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Error {response.status} for {url}")
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                        continue
                    else:
                        return None
        except aiohttp.ClientPayloadError as e:
            if attempt < retries - 1:
                await asyncio.sleep(1 * (attempt + 1))  # Increasing backoff
                print(
                    f"Retrying... {retries - attempt - 1} attempts left. Error: {str(e)}"
                )
                continue
            else:
                print(f"Failed to fetch data from {url}. Error: {str(e)}")
                return None
        except aiohttp.ClientConnectorError as e:
            if attempt < retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                print(
                    f"Connection error. Retrying... {retries - attempt - 1} attempts left."
                )
                continue
            else:
                print(f"Connection error for {url}: {e}")
                return None
        except aiohttp.ServerDisconnectedError as e:
            if attempt < retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                print(
                    f"Server disconnected. Retrying... {retries - attempt - 1} attempts left."
                )
                continue
            else:
                print(f"Server disconnected for {url}: {e}")
                return None
        except aiohttp.SocketTimeoutError as e:
            if attempt < retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                print(
                    f"Socket timeout. Retrying... {retries - attempt - 1} attempts left."
                )
                continue
            else:
                print(f"Socket timeout error for {url}: {e}")
                return None
        except aiohttp.ClientError as e:
            print(f"Client error for {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")
            return None


async def _fetch_all_data(urls):
    # Use a longer timeout and keep connections alive
    conn = aiohttp.TCPConnector(limit=10, ssl=False)
    session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=60)

    async with aiohttp.ClientSession(
        timeout=session_timeout,
        connector=conn,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        },
    ) as session:
        tasks = [_fetch_data(session, url) for url in urls]
        results = await tqdm_asyncio.gather(*tasks, desc="Fetching data")

        # Filter out None results (failed requests)
        valid_results = [r for r in results if r is not None]

        if len(valid_results) < len(urls):
            print(
                f"Warning: {len(urls) - len(valid_results)} of {len(urls)} requests failed"
            )

        return valid_results


async def _statcast_date_range_helper(
    start_dt: str,
    end_dt: str,
    team: str = None,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.LazyFrame | pd.DataFrame:
    """
    Pulls statcast data for a date range.

    Args:
    start_dt: the start date in 'YYYY-MM-DD' format
    end_dt: the end date in 'YYYY-MM-DD' format
    team: the team abbreviation (e.g. 'WSH'). If None, data for all teams will be returned.

    Returns:
    A DataFrame of statcast data for the date range.
    """
    if start_dt is None or end_dt is None:
        raise ValueError("Both start_dt and end_dt must be provided.")
    print(f"Pulling data for date range: {start_dt} to {end_dt}.")
    start_dt, end_dt = _handle_dates(start_dt, end_dt)
    date_ranges = list(_create_date_ranges(start_dt, end_dt, 1))

    data_list = []

    urls = []
    for start, end in date_ranges:
        urls.append(
            ROOT_URL
            + DATE_RANGE.format(
                start_dt=start,
                end_dt=end,
                team=team if team is not None else "",
                pos="pitcher",
            )
        )

    # Use smaller batches to avoid overwhelming the server
    batch_size = 20
    schema = None

    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i : i + batch_size]
        print(
            f"Processing batch {i // batch_size + 1}/{(len(urls) + batch_size - 1) // batch_size}"
        )

        responses = await _fetch_all_data(batch_urls)

        for data in tqdm(responses, desc="Processing regular data"):
            try:
                # scan csv as lazyframe and drop columns that will always be null
                data = pl.scan_csv(data)
                if schema is None:
                    schema = data.collect_schema()
                else:
                    data = data.cast(schema)
                data_list.append(data)
            except Exception as e:
                print(f"Error processing data: {e}")
                continue

    if not data_list:
        print("No data was successfully retrieved.")
        # Return empty dataframe with similar schema
        return pl.LazyFrame() if not return_pandas else pd.DataFrame()

    print("Concatenating data.")
    df = pl.concat(data_list)
    print("Data concatenated.")
    if not extra_stats:
        print("Done")
        return df if not return_pandas else df.collect().to_pandas()
    else:
        return await _add_extra_stats(
            df,
            start_dt,
            end_dt,
            return_pandas=return_pandas,
            pos_in=["pitcher", "batter"],
        )


async def _statcast_single_batter_range_helper(
    start_dt: str,
    end_dt: str,
    player_id: int,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_dt is None or end_dt is None:
        raise ValueError("Both start_dt and end_dt must be provided.")
    print(f"Pulling data for date range: {start_dt} to {end_dt}.")
    start_dt, end_dt = _handle_dates(start_dt, end_dt)
    date_ranges = list(_create_date_ranges(start_dt, end_dt, 1))

    data_list = []
    urls = [
        ROOT_URL
        + DATE_RANGE_SINGLE_BATTER.format(
            start_dt=start,
            end_dt=end,
            batter_id=player_id,
            pos="batter",
            team="",
        )
        for start, end in date_ranges
    ]
    schema = None
    responses = await _fetch_all_data(urls)
    for data in tqdm(responses, desc="Processing regular data"):
        # scan csv as lazyframe and drop columns that will always be null
        data = pl.scan_csv(data)
        if schema is None:
            schema = data.collect_schema()
        else:
            data = data.cast(schema)
        data_list.append(data)
    print("Concatenating data.")
    df = pl.concat(data_list)
    print("Data concatenated.")
    if not extra_stats:
        print("Done")
        return df if not return_pandas else df.collect().to_pandas()
    else:
        return await _add_extra_stats(
            df, start_dt, end_dt, return_pandas=return_pandas, pos_in=["batter"]
        )


async def _statcast_single_pitcher_range_helper(
    start_dt: str,
    end_dt: str,
    player_id: int,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_dt is None or end_dt is None:
        raise ValueError("Both start_dt and end_dt must be provided.")
    print(f"Pulling data for date range: {start_dt} to {end_dt}.")
    start_dt, end_dt = _handle_dates(start_dt, end_dt)
    date_ranges = list(_create_date_ranges(start_dt, end_dt, 1))

    data_list = []
    urls = [
        ROOT_URL
        + DATE_RANGE_SINGLE_PITCHER.format(
            start_dt=start,
            end_dt=end,
            pitcher_id=player_id,
            pos="pitcher",
            team="",
        )
        for start, end in date_ranges
    ]
    schema = None
    responses = await _fetch_all_data(urls)
    for data in tqdm(responses, desc="Processing regular data"):
        # scan csv as lazyframe and drop columns that will always be null
        data = pl.scan_csv(data)
        if schema is None:
            schema = data.collect_schema()
        else:
            data = data.cast(schema)
        data_list.append(data)
    print("Concatenating data.")
    df = pl.concat(data_list)
    print("Data concatenated.")
    if not extra_stats:
        print("Done")
        return df if not return_pandas else df.collect().to_pandas()
    else:
        return await _add_extra_stats(
            df, start_dt, end_dt, return_pandas=return_pandas, pos_in=["pitcher"]
        )


async def _add_extra_stats(
    df: pl.LazyFrame,
    start_dt: dt.date,
    end_dt: dt.date,
    return_pandas: bool = False,
    pos_in: List[str] = ["pitcher", "batter"],
) -> pl.LazyFrame | pd.DataFrame:
    df_list = []
    urls = [
        ROOT_URL + EXTRA_STATS.format(pos=pos, start_dt=start_dt, end_dt=end_dt)
        for pos in pos_in
    ]
    responses = await _fetch_all_data(urls)
    for data in tqdm(responses, desc="Processing extra data"):
        data = pl.scan_csv(data)
        df_list.append(data)
    df = df.with_columns(
        pl.col("pitcher").cast(pl.Int64).alias("pitcher"),
        pl.col("batter").cast(pl.Int64).alias("batter"),
    )
    if pos_in == ["pitcher", "batter"]:
        p_df = df_list[0]
        p_df = p_df.drop("player_name").rename(lambda x: f"{x}_pitcher")
        b_df = df_list[1]
        b_df = b_df.drop("player_name").rename(lambda x: f"{x}_batter")
        print("Joining data.")
        df = df.join(p_df, left_on="pitcher", right_on="player_id_pitcher", how="left")
        df = df.join(b_df, left_on="batter", right_on="player_id_batter", how="left")
        print("Done")
    elif pos_in == ["pitcher"]:
        p_df = df_list[0]
        p_df = p_df.drop("player_name").rename(lambda x: f"{x}_pitcher")
        print("Joining data.")
        df = df.join(p_df, left_on="pitcher", right_on="player_id_pitcher", how="left")
        print("Done")
    elif pos_in == ["batter"]:
        b_df = df_list[0]
        b_df = b_df.drop("player_name").rename(lambda x: f"{x}_batter")
        print("Joining data.")
        df = df.join(b_df, left_on="batter", right_on="player_id_batter", how="left")
    return df if not return_pandas else df.collect().to_pandas()


def _handle_dates(start_dt: str, end_dt: str) -> Tuple[dt.date, dt.date]:
    """
    Helper function to handle date inputs.

    Args:
    start_dt: the start date in 'YYYY-MM-DD' format
    end_dt: the end date in 'YYYY-MM-DD' format

    Returns:
    A tuple of datetime.date objects for the start and end dates.
    """
    start_dt_date = dt.datetime.strptime(start_dt, STATCAST_DATE_FORMAT).date()
    end_dt_date = dt.datetime.strptime(end_dt, STATCAST_DATE_FORMAT).date()
    if start_dt_date > end_dt_date:
        raise ValueError("start_dt must be before end_dt.")
    return start_dt_date, end_dt_date


# this function comes from https://github.com/jldbc/pybaseball/blob/master/pybaseball/statcast.py
def _create_date_ranges(
    start: dt.date, stop: dt.date, step: int, verbose: bool = True
) -> Iterator[Tuple[dt.date, dt.date]]:
    """
    Iterate over dates. Skip the offseason dates. Returns a pair of dates for beginning and end of each segment.
    Range is inclusive of the stop date.
    If verbose is enabled, it will print a message if it skips offseason dates.
    This version is Statcast specific, relying on skipping predefined dates from STATCAST_VALID_DATES.
    """
    if start == stop:
        yield start, stop
        return
    low = start

    while low <= stop:
        date_span = low.replace(month=3, day=15), low.replace(month=11, day=15)
        season_start, season_end = YEAR_RANGES.get(low.year, date_span)
        if low < season_start:
            low = season_start
        elif low > season_end:
            low, _ = YEAR_RANGES.get(
                low.year + 1, (dt.date(month=3, day=15, year=low.year + 1), None)
            )

        if low > stop:
            return
        high = min(low + dt.timedelta(step - 1), stop)
        yield low, high
        low += dt.timedelta(days=step)
