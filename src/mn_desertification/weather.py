"""The weather model: how much of each site's year-to-year change the weather explains.

Within each ecological zone, the model is

    log10(value) = the site's own average + b × log10(growing-season rain)
                   [+ c × summer temperature] + remainder

The site's own average absorbs the fact that sites differ. ``b`` (and ``c``)
are shared by all sites in a zone: with only ten years, a site's own fit would
partly absorb the decline the study looks for (Wessels et al. 2012). There is
no effect for each year, which would absorb any decline shared by the whole
country. The remainder is what the weather leaves unexplained.

Rain only was the planned model. Summer temperature was added as a second model
after the site trends showed a shared pattern, and both are reported.
"""

from typing import NamedTuple

import numpy as np
import pandas as pd


class WeatherFit(NamedTuple):
    """The result of ``fit_weather_model``."""

    remainders: pd.DataFrame
    """The input rows, with the centred variables and a ``remainder`` column."""

    effects: pd.DataFrame
    """One row per zone: ``b_rain``, ``c_temp`` if used, ``R2`` and the number of site-years."""


def fit_weather_model(table: pd.DataFrame, value_col: str, with_temp: bool = True) -> WeatherFit:
    """Fit the weather model to ``value_col``, zone by zone.

    ``table`` needs ``gid``, ``zone``, ``rain_growing``, ``value_col`` and,
    with temperature, ``temp_summer``. Values must be positive, so floor
    biomass first. Rows missing any of these are dropped.

    Subtracting each site's mean from every variable and fitting without an
    intercept gives the same slopes as fitting a separate intercept for each
    site. ``R2`` is the share of the sites' year-to-year variation, around
    their own averages, that the weather explains.
    """
    fitted = table.copy()
    fitted["y"] = np.log10(fitted[value_col])
    fitted["rain"] = np.log10(fitted["rain_growing"])
    drivers = ["rain"] + (["temp_summer"] if with_temp else [])
    columns = ["y", *drivers]
    fitted = fitted.dropna(subset=columns)

    # Each site against its own average
    for column in columns:
        fitted[column] = fitted[column] - fitted.groupby("gid")[column].transform("mean")

    effects = []
    for zone, group in fitted.groupby("zone", observed=True):
        X = group[drivers].to_numpy()
        y = group["y"].to_numpy()
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)  # least squares with no intercept
        remainder = y - X @ coef
        fitted.loc[group.index, "remainder"] = remainder
        effects.append({
            "zone": zone,
            "b_rain": coef[0],
            **({"c_temp": coef[1]} if with_temp else {}),
            "R2": 1 - (remainder ** 2).sum() / (y ** 2).sum(),
            "site-years": len(group),
        })
    return WeatherFit(fitted, pd.DataFrame(effects))


def weather_remainders(table: pd.DataFrame, value_col: str, with_temp: bool = True) -> pd.DataFrame:
    """The rows of ``table`` with a ``remainder`` column from ``fit_weather_model``."""
    return fit_weather_model(table, value_col, with_temp).remainders
