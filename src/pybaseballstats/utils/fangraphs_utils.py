import random
import time
from datetime import datetime
from typing import Any, Generic, Literal, Tuple, TypeVar, Union

from curl_cffi import requests
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.sync_api import (
    sync_playwright,
)
from playwright_stealth import Stealth  # type: ignore[import-untyped]

from pybaseballstats.consts.fangraphs_consts import (
    FangraphsBattingPosTypes,
    FangraphsLeaderboardTeams,
)


def validate_min_pa_param(min_pa: Union[int, str]) -> str:
    if isinstance(min_pa, int):
        if min_pa < 0:
            raise ValueError("min_pa must be a non-negative integer or 'y'")
        return str(min_pa)
    elif isinstance(min_pa, str):
        if min_pa.lower() != "y":
            raise ValueError("min_pa string value must be 'y'")
        return "y"
    else:
        raise ValueError("min_pa must be either a non-negative integer or 'y'")


def validate_pos_param(pos: FangraphsBattingPosTypes) -> str:
    if type(pos) is not FangraphsBattingPosTypes:
        raise ValueError("pos must be a FangraphsBattingPosTypes enum value")
    elif pos is None:
        return FangraphsBattingPosTypes.ALL.value
    else:
        return pos.value


def validate_hand_param(handedness: Literal["L", "R", "S", ""]) -> str:
    if handedness not in ["L", "R", "S", ""]:
        raise ValueError("handedness must be one of ['L', 'R', 'S', '']")

    return handedness


def validate_age_params(min_age: int, max_age: int) -> None:
    if not (14 <= min_age <= 56):
        raise ValueError("min_age must be between 14 and 56")
    if not (14 <= max_age <= 56):
        raise ValueError("max_age must be between 14 and 56")
    if min_age > max_age:
        raise ValueError("min_age cannot be greater than max_age")
    return


def validate_ind_param(split_seasons: bool) -> str:
    if not isinstance(split_seasons, bool):
        raise ValueError("split_seasons must be a boolean value")
    if split_seasons:
        return "1"
    else:
        return "0"


def validate_seasons_param(
    start_season: int | None, end_season: int | None
) -> Tuple[str, str]:
    current_year = datetime.now().year

    # Check if only one parameter is provided for single season
    if start_season is not None and end_season is None:
        assert start_season is not None  # for mypy
        if start_season < 1871 or start_season > current_year:
            raise ValueError(f"start_season must be between 1871 and {current_year}")
        print(
            "End season not provided, doing a single year search using the start season param."
        )
        return str(start_season), str(start_season)
    elif start_season is None and end_season is not None:
        assert end_season is not None  # for mypy
        if end_season < 1871 or end_season > current_year:
            raise ValueError(f"end_season must be between 1871 and {current_year}")
        print(
            "Start season not provided, doing a single year search using the end season param."
        )
        return str(end_season), str(end_season)
    elif start_season is None and end_season is None:
        raise ValueError("At least one season must be provided")
    assert start_season is not None and end_season is not None  # for mypy
    # Both parameters provided - validate range
    if start_season < 1871 or start_season > current_year:
        raise ValueError(f"start_season must be between 1871 and {current_year}")
    if end_season < 1871 or end_season > current_year:
        raise ValueError(f"end_season must be between 1871 and {current_year}")
    if start_season > end_season:
        raise ValueError("start_season cannot be greater than end_season")
    return str(start_season), str(end_season)


def validate_league_param(league: Literal["", "al", "nl"]) -> str:
    if league not in ["", "al", "nl"]:
        raise ValueError("league must be one of '', 'al', or 'nl'")
    return league


def validate_team_stat_split_param(
    team: FangraphsLeaderboardTeams, stat_split: str
) -> str:
    # handle team and stat_split together
    if stat_split and stat_split not in ["player", "team", "league"]:
        raise ValueError("stat_split must be one of 'player', 'team', or 'league'")
    if stat_split == "player":
        stat_split = ""
    elif stat_split is None:
        print("No stat_split provided, defaulting to player stats")
        stat_split = ""
    elif stat_split == "team":
        stat_split = "ts"
    elif stat_split == "league":
        stat_split = "ss"
    if team:
        assert isinstance(team, FangraphsLeaderboardTeams)
        team_value = str(team.value)
    else:
        team_value = ""
    team_together = ""
    if stat_split == "":
        team_together = team_value
    else:
        team_together = f"{team_value},{stat_split}"
    return team_together


def validate_active_roster_param(active_roster_only: bool) -> str:
    assert isinstance(active_roster_only, bool), (
        "active_roster_only must be a boolean value"
    )
    if active_roster_only:
        return "1"
    return "0"


def validate_season_type(season_type: str) -> str:
    if not season_type:
        print("No season_type provided, defaulting to regular season stats")
        return ""
    if season_type not in [
        "regular",
        "all_postseason",
        "world_series",
        "championship_series",
        "division_series",
        "wild_card",
    ]:
        raise ValueError("Invalid season_type")

    match season_type:
        case "regular":
            return ""
        case "all_postseason":
            return "Y"
        case "world_series":
            return "W"
        case "championship_series":
            return "L"
        case "division_series":
            return "D"
        case "wild_card":
            return "F"
    raise Exception("Unreachable code reached in validate_season_type")


def validate_dates(start_date: str | None, end_date: str | None) -> Tuple[str, str]:
    if not start_date:
        raise ValueError("start_date must be provided")
    if not end_date:
        print("No end date provided, defaulting to today's date")
        end_date = datetime.today().strftime("%Y-%m-%d")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    assert start_dt is not None, (
        "Could not parse start_date, ensure it is in 'YYYY-MM-DD' format"
    )
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    assert end_dt is not None, (
        "Could not parse end_date, ensure it is in 'YYYY-MM-DD' format"
    )
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date")
    # ensure year range is valid
    if start_dt.year < 1871:
        raise ValueError("start_date year must be 1871 or later")
    current_year = datetime.now().year
    if start_dt.year > current_year:
        raise ValueError(f"end_date year cannot be later than {current_year}")
    if end_dt.year < 1871:
        raise ValueError("end_date year must be 1871 or later")
    if end_dt.year > current_year:
        raise ValueError(f"end_date year cannot be later than {current_year}")
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")


def validate_seasons_and_dates_together(
    start_season: int | None,
    end_season: int | None,
    start_date: str | None,
    end_date: str | None,
) -> bool:
    if (start_season is not None) and (start_date is not None):
        raise ValueError(
            "Specify either seasons (start_season, end_season) OR dates (start_date, end_date), but not both."
        )
    if (start_season is None) and (start_date is None):
        raise ValueError(
            "You must provide either a start or end season (start_season, end_season) OR a start date (start_date, end_date)."
        )
    if start_season:
        # using seasons
        return True
    else:
        # using dates
        return False


# https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
T = TypeVar("T")


class Singleton(Generic[T]):
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated: type[T]) -> None:
        self._decorated = decorated
        self._instance: T | None = None

    def instance(self) -> T:
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        if self._instance is None:
            self._instance = self._decorated()
        return self._instance

    def __call__(self) -> None:
        raise TypeError("Singletons must be accessed through `instance()`.")

    def __instancecheck__(self, inst: object) -> bool:
        return isinstance(inst, self._decorated)


@Singleton
class FGSession:
    """
    A singleton class to manage requests and automated
    Cloudflare bypassing via Playwright.
    """

    def __init__(
        self,
    ) -> None:

        # Initialize pure curl_cffi session with no manual headers
        self.session: requests.Session = requests.Session()

    def _is_cloudflare_challenge(self, response: requests.Response) -> bool:
        """Check if the response is a Cloudflare block/challenge."""
        if response.status_code in (403, 503):
            return True
        # Cloudflare challenges often return 200 but contain specific text
        text = response.text.lower()
        if (
            "just a moment" in text
            or "attention required" in text
            or "cloudflare" in text
        ):
            return True
        return False

    def _solve_cloudflare_challenge(self, url: str) -> None:
        """Spin up an ephemeral, stealthed Playwright instance to bypass Cloudflare."""
        print(f"\n[DEBUG] === Initiating Cloudflare Bypass for {url} ===")

        try:
            with Stealth().use_sync(sync_playwright()) as p:
                print(
                    "[DEBUG] Launching visible browser with automation flags disabled..."
                )
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-popup-blocking",
                    ],
                )

                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                )
                page = context.new_page()

                print("[DEBUG] Navigating to target URL...")
                page.goto(url, wait_until="domcontentloaded")

                start_time = time.time()
                max_wait = 45

                while time.time() - start_time < max_wait:
                    # 1. Victory Check
                    if page.locator("table, #footer").count() > 0:
                        print("\n[SUCCESS] Clearance achieved! Target page loaded.")
                        break

                    # 2. Element Scans
                    cf_iframes = page.frame_locator(
                        "iframe[src*='challenges'], iframe[src*='turnstile']"
                    )
                    shadow_turnstile = page.locator(
                        "input[name='cf-turnstile-response']"
                    )

                    iframe_count = page.locator(
                        "iframe[src*='challenges'], iframe[src*='turnstile']"
                    ).count()
                    shadow_count = shadow_turnstile.count()

                    print(
                        f"[DEBUG] Scan -> Iframes found: {iframe_count} | Hidden Shadow inputs found: {shadow_count}"
                    )

                    try:
                        target_x, target_y = None, None

                        # Scenario A: Closed Shadow DOM
                        if shadow_count > 0:
                            parent_div = shadow_turnstile.first.locator("..")
                            box = parent_div.bounding_box()
                            print(f"[DEBUG] Shadow DOM parent bounding box: {box}")

                            if box and box["width"] > 0:
                                target_x = box["x"] + 30 + random.uniform(-5, 5)
                                target_y = (
                                    box["y"]
                                    + (box["height"] / 2)
                                    + random.uniform(-5, 5)
                                )
                                print(
                                    f"[DEBUG] Calculated Shadow Target: X={target_x:.1f}, Y={target_y:.1f}"
                                )

                        # Scenario B: Standard iframe
                        elif iframe_count > 0:
                            checkbox = cf_iframes.locator(
                                ".cb-c, input[type='checkbox']"
                            ).first
                            if checkbox.is_visible(timeout=2000):
                                box = checkbox.bounding_box()
                                print(
                                    f"[DEBUG] Standard Iframe checkbox bounding box: {box}"
                                )
                                if box:
                                    target_x = (
                                        box["x"]
                                        + (box["width"] / 2)
                                        + random.uniform(-5, 5)
                                    )
                                    target_y = (
                                        box["y"]
                                        + (box["height"] / 2)
                                        + random.uniform(-5, 5)
                                    )
                                    print(
                                        f"[DEBUG] Calculated Iframe Target: X={target_x:.1f}, Y={target_y:.1f}"
                                    )

                        # 3. Execution
                        if target_x is not None and target_y is not None:
                            print(
                                "\n[ACTION] Target locked. Injecting visual debug dot..."
                            )

                            page.wait_for_timeout(random.randint(1000, 2000))

                            print("[ACTION] Moving mouse...")
                            page.mouse.move(
                                target_x, target_y, steps=random.randint(15, 30)
                            )
                            page.wait_for_timeout(random.randint(200, 500))

                            print("[ACTION] Clicking...")
                            page.mouse.down()
                            page.wait_for_timeout(random.randint(40, 120))
                            page.mouse.up()

                            page.mouse.move(
                                target_x + random.randint(100, 300),
                                target_y + random.randint(100, 300),
                                steps=random.randint(10, 20),
                            )

                            print(
                                "[ACTION] Click complete. Waiting 4 seconds for Cloudflare response...\n"
                            )
                            page.wait_for_timeout(4000)
                            continue

                    except Exception as e:
                        print(f"[DEBUG] Exception during targeting/clicking: {e}")

                    page.wait_for_timeout(1500)

                if page.locator("table, #footer").count() == 0:
                    print(
                        "\n[WARNING] Loop timed out. Saving debug screenshot to 'cf_timeout_debug.png'"
                    )

                print("[DEBUG] Extracting cookies...")
                for cookie in context.cookies():
                    self.session.cookies.set(
                        cookie["name"], cookie["value"], domain=cookie["domain"]
                    )
                print("[DEBUG] === Bypass Process Complete ===\n")

        except PlaywrightTimeoutError:
            print("\n[ERROR] Playwright timed out completely.")
        except Exception as e:
            print(f"\n[ERROR] Critical failure: {e}")

    def get(self, url: str, **kwargs: Any) -> requests.Response | None:
        """Make an HTTP request with automatic Waterfall escalation."""
        # _ensure_bref_enabled()

        try:
            # ATTEMPT 1: Fast curl_cffi
            resp = self.session.get(url, impersonate="chrome120", **kwargs)

            # Check for block
            if self._is_cloudflare_challenge(resp):
                # ATTEMPT 2: The Waterfall Escalation
                self._solve_cloudflare_challenge(url)

                resp = self.session.get(url, impersonate="chrome120", **kwargs)

            resp.raise_for_status()
            return resp

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Received 429 Too Many Requests for {url}. Backing off.")
            else:
                print(f"HTTP Error fetching {url}: {e}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

        return None


# def fangraphs_fielding_input_val(
#     start_year: Union[int, None] = None,
#     end_year: Union[int, None] = None,
#     min_inn: Union[str, int] = "y",
#     stat_types: List[FangraphsFieldingStatType] = None,
#     active_roster_only: bool = False,
#     team: FangraphsLeaderboardTeams = FangraphsLeaderboardTeams.ALL,
#     league: Literal["nl", "al", ""] = "",
#     fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
# ):
#     if not (start_year and end_year):
#         raise ValueError("You must provide (start_year, end_year).")

#     # Validate seasons if provided
#     if start_year and end_year:
#         if start_year > end_year:
#             raise ValueError(
#                 f"start_year ({start_year}) cannot be after end_year ({end_year})."
#             )
#         print(f"Using season range: {start_year} to {end_year}")

#     # min_pa validation
#     if isinstance(min_inn, str):
#         if min_inn not in ["y"]:
#             raise ValueError("If min_inn is a string, it must be 'y' (qualified).")
#     elif isinstance(min_inn, int):
#         if min_inn < 0:
#             raise ValueError("min_inn must be a positive integer.")
#     else:
#         raise ValueError("min_inn must be a string or integer.")

#     # fielding_position validation
#     if not isinstance(fielding_position, FangraphsBattingPosTypes):
#         raise ValueError(
#             "fielding_position must be a valid FangraphsBattingPosTypes value"
#         )

#     # active_roster_only validation
#     if not isinstance(active_roster_only, bool):
#         raise ValueError("active_roster_only must be a boolean value.")
#     if active_roster_only:
#         print("Only active roster players will be included.")
#         active_roster_only = 1
#     else:
#         print("All players will be included.")
#         active_roster_only = 0

#     # team validation
#     if not isinstance(team, FangraphsLeaderboardTeams):
#         raise ValueError("team must be a valid FangraphsLeaderboardTeams value")
#     else:
#         print(f"Filtering by team: {team}")
#         team = team.value
#     # league validation
#     if league not in ["nl", "al", ""]:
#         raise ValueError("league must be 'nl', 'al', or an empty string.")
#     if league:
#         print(f"Filtering by league: {league}")

#     stat_cols = set()
#     # stat_types validation
#     if stat_types is None:
#         for stat_type in FangraphsFieldingStatType:
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     else:
#         for stat_type in stat_types:
#             if not isinstance(stat_type, FangraphsFieldingStatType):
#                 raise ValueError(
#                     "stat_types must be a list of valid FangraphsFieldingStatType values"
#                 )
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     stat_types = list(stat_cols)
#     return (
#         start_year,
#         end_year,
#         min_inn,
#         fielding_position,
#         active_roster_only,
#         team,
#         league,
#         stat_types,
#     )


# def fangraphs_pitching_range_input_val(
#     start_date: Union[str, None] = None,
#     end_date: Union[str, None] = None,
#     start_year: Union[int, None] = None,
#     end_year: Union[int, None] = None,
#     min_ip: Union[str, int] = "y",
#     stat_types: List[FangraphsPitchingStatType] = None,
#     active_roster_only: bool = False,
#     team: FangraphsLeaderboardTeams = FangraphsLeaderboardTeams.ALL,
#     league: Literal["nl", "al", ""] = "",
#     min_age: Optional[int] = None,
#     max_age: Optional[int] = None,
#     pitching_hand: Literal["R", "L", "S", ""] = "",
#     starter_reliever: Literal["sta", "rel", "pit"] = "pit",
#     split_seasons: bool = False,
# ):
#     if (start_date and end_date) and (start_year and end_year):
#         raise ValueError(
#             "Specify either (start_date, end_date) OR (start_year, end_year), but not both."
#         )

#     if not (start_date and end_date) and not (start_year and end_year):
#         raise ValueError(
#             "You must provide either (start_date, end_date) OR (start_year, end_year)."
#         )

#     # Validate and convert dates if provided
#     if start_date and end_date:
#         start_date, end_date = fangraphs_validate_dates(start_date, end_date)
#         start_year = None
#         end_year = None
#         print(f"Using date range: {start_date} to {end_date}")

#     # Validate seasons if provided
#     if start_year and end_year:
#         if start_year > end_year:
#             raise ValueError(
#                 f"start_season ({start_year}) cannot be after end_season ({end_year})."
#             )
#         print(f"Using season range: {start_year} to {end_year}")
#         start_date = None
#         end_date = None

#     if isinstance(min_ip, str):
#         if min_ip not in ["y"]:
#             raise ValueError("If min_ip is a string, it must be 'y' (qualified).")
#     elif isinstance(min_ip, int):
#         if min_ip < 0:
#             raise ValueError("min_ip must be a positive integer.")
#     else:
#         raise ValueError("min_ip must be a string or integer.")

#     if stat_types is None:
#         stat_types = [stat for stat in list(FangraphsPitchingStatType)]
#     else:
#         if not stat_types:
#             raise ValueError("stat_types must not be an empty list.")
#         for stat in stat_types:
#             if stat not in list(FangraphsPitchingStatType):
#                 raise ValueError(f"Invalid stat type: {stat}")

#     # active_roster_only validation
#     if not isinstance(active_roster_only, bool):
#         raise ValueError("active_roster_only must be a boolean value.")
#     if active_roster_only:
#         print("Only active roster players will be included.")
#         active_roster_only = 1
#     else:
#         print("All players will be included.")
#         active_roster_only = 0

#     # team validation
#     if not isinstance(team, FangraphsLeaderboardTeams):
#         raise ValueError("team must be a valid FangraphsLeaderboardTeams value")
#     else:
#         print(f"Filtering by team: {team}")
#         team = team.value
#     # league validation
#     if league not in ["nl", "al", ""]:
#         raise ValueError("league must be 'nl', 'al', or an empty string.")
#     if league:
#         print(f"Filtering by league: {league}")

#     if (min_age is not None and max_age is None) or (
#         min_age is None and max_age is not None
#     ):
#         raise ValueError("Both min_age and max_age must be provided or neither")
#     if min_age is None:
#         min_age = 14
#     if max_age is None:
#         max_age = 56
#     if min_age > max_age:
#         raise ValueError(
#             f"min_age ({min_age}) cannot be greater than max_age ({max_age})"
#         )
#     if min_age < 14:
#         raise ValueError("min_age must be at least 14")
#     if max_age > 56:
#         raise ValueError("max_age must be at most 56")

#     if pitching_hand not in ["R", "L", "S", ""]:
#         raise ValueError("pitching_hand must be 'R', 'L', 'S', or an empty string.")

#     if starter_reliever not in ["sta", "rel", "pit"]:
#         raise ValueError("starter_reliever must be 'sta', 'rel', or 'pit'.")
#     stat_cols = set()
#     # stat_types validation
#     if stat_types is None:
#         for stat_type in FangraphsPitchingStatType:
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     else:
#         for stat_type in stat_types:
#             if not isinstance(stat_type, FangraphsPitchingStatType):
#                 raise ValueError(
#                     "stat_types must be a list of valid FangraphsPitchingStatType values"
#                 )
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     stat_types = list(stat_cols)
#     assert isinstance(split_seasons, bool)
#     if split_seasons:
#         split_seasons = 1
#     else:
#         split_seasons = 0
#     return (
#         start_date,
#         end_date,
#         start_year,
#         end_year,
#         min_ip,
#         stat_types,
#         active_roster_only,
#         team,
#         league,
#         min_age,
#         max_age,
#         pitching_hand,
#         starter_reliever,
#         stat_types,
#         split_seasons,
#     )
