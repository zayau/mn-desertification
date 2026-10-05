"""Trend tests for sites and for yearly means.

Trends are fitted to remainders in log10 units. A slope ``s`` per year is
``10 * s`` per decade, and a change of ``v`` log10 per decade is a factor of
``10 ** v``, so -0.3 per decade is a halving.
"""

import numpy as np
import pandas as pd
from scipy import stats

from .rules import MIN_YEARS


def trend_test(values: np.ndarray, years: np.ndarray):
    """Least-squares slope and one-sided p-value for a decline, for every row.

    ``values`` is a sites × years array with NaN for missing years, and
    ``years`` the matching years. Each row gets its own straight line through
    the years it has. The p-value is the chance of a slope this low if the row
    had no trend, from a t-test with n - 2 degrees of freedom. It equals
    ``scipy.stats.linregress(..., alternative="less")`` row by row, computed
    for all rows at once.

    Returns two arrays: the slope per year and the p-value.
    """
    has = ~np.isnan(values)
    n = has.sum(axis=1)
    x = np.where(has, years, np.nan)  # the years, blanked where missing
    dx = x - np.nanmean(x, axis=1, keepdims=True)
    dy = values - np.nanmean(values, axis=1, keepdims=True)
    sxx = np.nansum(dx ** 2, axis=1)
    slope = np.nansum(dx * dy, axis=1) / sxx
    resid = dy - slope[:, None] * dx
    se = np.sqrt(np.nansum(resid ** 2, axis=1) / (n - 2) / sxx)
    p_decline = stats.t.cdf(slope / se, df=n - 2)
    return slope, p_decline


def percent_per_decade(log10_per_decade):
    """Convert a change in log10 per decade to percent per decade."""
    return 100 * (10 ** np.asarray(log10_per_decade) - 1)


def yearly_mean(remainders: pd.DataFrame, column: str = "remainder") -> pd.Series:
    """The mean of ``column`` over all sites in each year."""
    return remainders.groupby("year")[column].mean()


def mean_trend(remainders: pd.DataFrame, column: str = "remainder"):
    """Trend of the yearly mean of all sites, per decade, with its 95% range.

    The range comes from the least-squares fit through the yearly means. It
    covers the trends the data cannot rule out: if it contains zero, the data
    cannot tell a decline from no change.

    Returns three numbers: the trend, and the low and high ends of the range,
    all in log10 per decade.
    """
    means = yearly_mean(remainders, column)
    fit = stats.linregress(means.index, means.values)
    margin = stats.t.ppf(0.975, len(means) - 2) * fit.stderr
    return 10 * fit.slope, 10 * (fit.slope - margin), 10 * (fit.slope + margin)


def remainder_grid(remainders: pd.DataFrame, column: str = "remainder") -> pd.DataFrame:
    """The remainders as a sites × years table, NaN where a year is missing."""
    return remainders.pivot(index="gid", columns="year", values=column)


def site_trends(remainders: pd.DataFrame, column: str = "remainder", min_years: int = MIN_YEARS) -> pd.DataFrame:
    """A trend for every site with at least ``min_years`` years.

    Two slopes per site: least squares, with its one-sided p-value for a
    decline, and Theil–Sen, the median of the slopes between all pairs of
    years, which resists outliers. Returns one row per site with ``n_years``,
    ``slope``, ``sen_slope`` (log10 per year), ``p_decline``, ``decade``
    (log10 per decade), ``pct_decade`` and ``sen_pct_decade``.
    """
    grid = remainder_grid(remainders, column)
    n_years = grid.notna().sum(axis=1)
    grid = grid[n_years >= min_years]
    years = grid.columns.to_numpy()
    slope, p_decline = trend_test(grid.to_numpy(), years)

    sen_slope = []
    for values in grid.to_numpy():
        has = ~np.isnan(values)
        sen_slope.append(stats.theilslopes(values[has], years[has]).slope)

    trends = pd.DataFrame({
        "n_years": n_years[grid.index].to_numpy(),
        "slope": slope,
        "sen_slope": sen_slope,
        "p_decline": p_decline,
    }, index=grid.index)
    trends["decade"] = 10 * trends["slope"]
    trends["pct_decade"] = percent_per_decade(trends["decade"])
    trends["sen_pct_decade"] = percent_per_decade(10 * trends["sen_slope"])
    return trends.reset_index()
