"""Satellite observations at the sites, after the extraction: which ones count, and how many there are.

The functions here work on the tables that ``scripts/extract_landsat.py``
saves. None of them connects to Earth Engine.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from .paths import PROCESSED_DIR
from .rules import FOOTPRINT_M, LANDSAT7_UNTIL, MIN_CLEAR, SEASON_FIRST, SEASON_LAST, TO_LANDSAT7

# The side of a Landsat pixel, in metres.
LANDSAT_PIXEL_M = 30


def read_landsat(folder: Path | None = None) -> pd.DataFrame:
    """Every saved Landsat observation, from the files of ``scripts/extract_landsat.py``.

    One row per sensor, site, radius and overpass, as
    ``satellite.landsat_observations`` describes, with ``sensor`` added.
    """
    folder = PROCESSED_DIR / "landsat" if folder is None else Path(folder)
    tables = [pd.read_csv(file) for file in sorted(folder.glob("landsat*.csv"))]
    # A summer with no scenes leaves a file with no rows
    table = pd.concat([table for table in tables if len(table)], ignore_index=True)
    # Some files hold times with fractions of a second and some without
    table["time"] = pd.to_datetime(table["time"], format="ISO8601")
    return table


def add_clear_share(observations: pd.DataFrame, pixel_m: float = LANDSAT_PIXEL_M) -> pd.DataFrame:
    """Add ``clear_share``: the clear part of each circle, as a share of the whole circle.

    ``clear_pixels`` counts the clear pixels inside the circle, and the whole
    circle holds pi times the radius squared, over the area of a pixel. Earth
    Engine draws the circle with straight sides, so a fully clear circle comes
    out just under 1.
    """
    circle_pixels = np.pi * observations["radius_m"] ** 2 / pixel_m ** 2
    return observations.assign(clear_share=observations["clear_pixels"] / circle_pixels)


def clearest_per_day(observations: pd.DataFrame) -> pd.DataFrame:
    """One observation per sensor, site, radius and day: the clearest.

    Where an overpass changes map zone, a site in the overlap of two scenes is
    extracted twice for the same day. The row with more clear pixels is kept.
    """
    by_clearness = observations.assign(day=observations["time"].dt.floor("D")).sort_values(
        "clear_pixels", ascending=False, kind="stable")
    kept = by_clearness.drop_duplicates(["sensor", "gid", "radius_m", "day"]).drop(columns="day")
    return kept.sort_values(["sensor", "gid", "radius_m", "time"], ignore_index=True)


def in_season(observations: pd.DataFrame, first: tuple = SEASON_FIRST, last: tuple = SEASON_LAST) -> pd.DataFrame:
    """The observations from ``first`` to ``last``, both (month, day) and both included, with their ``year``."""
    month_day = observations["time"].dt.month * 100 + observations["time"].dt.day
    kept = observations[month_day.between(first[0] * 100 + first[1], last[0] * 100 + last[1])]
    return kept.assign(year=kept["time"].dt.year)


def long_record_start(sites_with_value: pd.Series, needed: float) -> int | None:
    """The first year from which every year has at least ``needed`` sites with a value.

    ``sites_with_value`` is indexed by year. A year that is left out counts as
    having no site. Returns None if the last year itself falls short.
    """
    years = range(int(sites_with_value.index.min()), int(sites_with_value.index.max()) + 1)
    short = sites_with_value.reindex(years, fill_value=0) < needed
    if short.iloc[-1]:
        return None
    # The record starts the year after the last year that falls short
    return int(short[short].index.max()) + 1 if short.any() else years[0]


def with_indices(observations: pd.DataFrame, to_landsat7: bool = True, conversions: dict | None = None) -> pd.DataFrame:
    """The observations with NDVI and MSAVI computed from the mean reflectances of each circle.

    The files also hold the mean of the pixels' own indices, as ``ndvi`` and
    ``msavi``. Those are renamed ``ndvi_pixels`` and ``msavi_pixels``, and
    ``ndvi`` and ``msavi`` become the indices of the mean ``red`` and ``nir``,
    as a sensor with the circle as its footprint would measure them.

    The reflectance is first put on the Landsat 7 scale. ``conversions`` gives
    the line for each sensor and band, as ``{sensor: {"red": (intercept,
    slope), "nir": (intercept, slope)}}``; a sensor that is left out stays as
    measured. With no ``conversions``, ``to_landsat7`` applies the published
    lines to Landsat 8 and 9 (``rules.TO_LANDSAT7``) or, if False, leaves every
    sensor as measured. The pixel means are never converted.
    """
    if conversions is None:
        conversions = {"landsat8": TO_LANDSAT7, "landsat9": TO_LANDSAT7} if to_landsat7 else {}
    table = observations.rename(columns={"ndvi": "ndvi_pixels", "msavi": "msavi_pixels"})
    red, nir = table["red"].copy(), table["nir"].copy()
    for sensor, lines in conversions.items():
        rows = table["sensor"] == sensor
        red[rows] = lines["red"][0] + lines["red"][1] * red[rows]
        nir[rows] = lines["nir"][0] + lines["nir"][1] * nir[rows]
    ndvi = (nir - red) / (nir + red)
    msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2
    return table.assign(red=red, nir=nir, ndvi=ndvi, msavi=msavi)


def sensor_pairs(observations: pd.DataFrame, first_sensor: str, second_sensor: str, days: int = 8) -> pd.DataFrame:
    """Observations of two sensors at the same site and circle, at most ``days`` days apart.

    Returns one row per pair, with the columns of each observation ending in
    ``_first`` and ``_second``, and ``days_apart``, the second sensor's day
    minus the first's. An observation with several partners appears in
    several pairs.
    """
    wanted = ["gid", "radius_m", "time", "red", "nir", "ndvi", "msavi"]
    first = observations.loc[observations["sensor"] == first_sensor, wanted]
    second = observations.loc[observations["sensor"] == second_sensor, wanted]
    # Pairing within the year keeps the table small; the extraction holds June to September only
    first = first.assign(year=first["time"].dt.year)
    second = second.assign(year=second["time"].dt.year)
    pairs = first.merge(second, on=["gid", "radius_m", "year"], suffixes=("_first", "_second"))
    pairs["days_apart"] = (pairs["time_second"].dt.floor("D") - pairs["time_first"].dt.floor("D")).dt.days
    return pairs[pairs["days_apart"].abs() <= days].reset_index(drop=True)


def fit_conversion(pairs: pd.DataFrame, onto: str = "first") -> dict:
    """The line for each band that puts one sensor's reflectance on the other's scale, fitted to their pairs.

    ``pairs`` comes from ``sensor_pairs``. ``onto`` names the sensor whose
    scale is kept, ``"first"`` or ``"second"``. The line is the reduced major
    axis: its slope is the ratio of the two standard deviations, and it passes
    through the two means. Unlike least squares, it allows for error in both
    sensors, so it does not flatten the scale. Returns ``{"red": (intercept,
    slope), "nir": (intercept, slope)}``, as ``with_indices`` takes them.
    """
    source = "second" if onto == "first" else "first"
    lines = {}
    for band in ["red", "nir"]:
        kept, converted = pairs[f"{band}_{onto}"], pairs[f"{band}_{source}"]
        slope = kept.std() / converted.std()
        lines[band] = (float(kept.mean() - slope * converted.mean()), float(slope))
    return lines


def read_conversions(path: Path | None = None) -> dict:
    """The lines that put each sensor on the Landsat 7 scale, as ``with_indices`` takes them.

    Reads the table that notebook 7 saves, ``landsat_conversions.csv``.
    """
    path = PROCESSED_DIR / "landsat_conversions.csv" if path is None else Path(path)
    conversions = {}
    for row in pd.read_csv(path).itertuples():
        conversions.setdefault(row.sensor, {})[row.band] = (row.intercept, row.slope)
    return conversions


def counting(observations: pd.DataFrame, radius_m: float = FOOTPRINT_M, min_clear: float = MIN_CLEAR,
             landsat7_until: int | None = LANDSAT7_UNTIL) -> pd.DataFrame:
    """The observations that count under the rules.

    ``observations`` needs ``clear_share`` (``add_clear_share``) and one row a
    day (``clearest_per_day``). Kept are the rows of the circle of
    ``radius_m``, with at least ``min_clear`` of it clear, and without Landsat
    7 after ``landsat7_until`` (None keeps every year).
    """
    kept = (observations["radius_m"] == radius_m) & (observations["clear_share"] >= min_clear)
    if landsat7_until is not None:
        kept &= ~((observations["sensor"] == "landsat7") & (observations["time"].dt.year > landsat7_until))
    return observations[kept]


def seasonal_values(observations: pd.DataFrame, index: str = "ndvi", how: str = "median",
                    first: tuple = SEASON_FIRST, last: tuple = SEASON_LAST) -> pd.DataFrame:
    """Each site's value for each year: the median, or the highest, of its observations in the season.

    The season runs from ``first`` to ``last``, both (month, day). Returns one
    row per site and year with ``gid``, ``year``, the ``index`` column and
    ``n_observations``. A site-year with no observation has no row.
    """
    by_site_year = in_season(observations, first, last).groupby(["gid", "year"])[index]
    summary = by_site_year.median() if how == "median" else by_site_year.max()
    return pd.DataFrame({index: summary, "n_observations": by_site_year.size()}).reset_index()
