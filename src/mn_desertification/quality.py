"""Very low values and likely recording errors.

docs/design.md sets the rules ("Very low values" and "Recording errors"), and
docs/data-checks.md, checks 2 and 4, gives the evidence.
"""

import numpy as np
import pandas as pd

from .rules import FLOOR, MAIN_YEARS


def floored_log(biomass: pd.Series, floor: float = FLOOR) -> pd.Series:
    """log10 of biomass, after raising values below ``floor`` to the floor.

    Values below 0.1 c/ha are almost all stand-ins for zero (0.01, 0.05 or
    0.001). The floor puts them level with near-empty sites recorded at the
    smallest step of 0.1, and keeps them from becoming large negative logs.
    """
    return np.log10(biomass.clip(lower=floor))


def add_rain_percent(site_year: pd.DataFrame, weather: pd.DataFrame, normal_years=MAIN_YEARS) -> pd.DataFrame:
    """Add each site-year's growing-season rain as a percent of its soum's normal.

    The normal is the soum's mean over ``normal_years``. Adds ``rain_normal``
    and ``rain_pct``, rounded to whole percent.
    """
    first, last = normal_years
    normal = weather[weather["year"].between(first, last)].groupby("asid")["rain_growing"].mean()
    with_rain = site_year.copy()
    with_rain["rain_normal"] = with_rain["asid"].map(normal)
    with_rain["rain_pct"] = (with_rain["rain_growing"] / with_rain["rain_normal"] * 100).round()
    return with_rain


def flag_recording_errors(site_year: pd.DataFrame, years=MAIN_YEARS, floor: float = FLOOR) -> pd.DataFrame:
    """Values in ``years`` that are likely recording errors.

    ``site_year`` needs ``gid``, ``year``, ``asid``, ``zone``, ``bms`` and
    ``rain_pct`` for the whole record. Two kinds of value are flagged:

    - A lone spike is more than 10 times (1 in log10) what the site's usual
      level and its zone's year predict, in a soum-year with less than 120% of
      normal rain, with no other site in the soum above 3 times (0.5 in log10)
      its expected value. Real good years lift several sites at once.
    - A value off the scale is more than twice the second-largest value in the
      whole record.

    Returns the flagged rows with ``gid``, ``year``, ``bms`` and ``flag``.
    """
    first, last = years
    main = site_year[site_year["year"].between(first, last)].copy()
    main["log_bms"] = floored_log(main["bms"], floor)

    # How far each value is from what its site and its zone's year predict (log10)
    main["site_anom"] = main["log_bms"] - main.groupby("gid")["log_bms"].transform("mean")
    main["excess"] = main["site_anom"] - main.groupby(["zone", "year"], observed=True)["site_anom"].transform("mean")

    # How many sites in each soum and year had more than 3 times what was expected
    main["big"] = main["excess"] > 0.5
    big_in_soum = main.groupby(["asid", "year"])["big"].transform("sum")

    lone_spike = (main["excess"] > 1) & (main["rain_pct"] < 120) & (big_in_soum == 1)
    second_largest = site_year["bms"].nlargest(2).iloc[1]
    off_scale = main["bms"] > 2 * second_largest

    main["flag"] = ""
    main.loc[lone_spike, "flag"] = "lone spike"
    main.loc[off_scale, "flag"] = "off the scale"
    return main.loc[main["flag"] != "", ["gid", "year", "bms", "flag"]]


def drop_flagged(table: pd.DataFrame, flags: pd.DataFrame) -> pd.DataFrame:
    """``table`` without the site-years listed in ``flags``."""
    flagged = set(zip(flags["gid"].astype(int), flags["year"].astype(int)))
    keep = [(gid, year) not in flagged for gid, year in zip(table["gid"], table["year"])]
    return table[keep]
