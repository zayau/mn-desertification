import numpy as np
import pandas as pd
from scipy import stats

from mn_desertification.trends import mean_trend, percent_per_decade, site_trends, trend_test

YEARS = np.arange(2011, 2021)


def test_trend_test_matches_linregress_row_by_row():
    rng = np.random.default_rng(0)
    values = rng.normal(size=(20, len(YEARS))) + 0.05 * (YEARS - 2015)
    values[3, [0, 4]] = np.nan  # two missing years in one row
    slope, p = trend_test(values, YEARS)
    for row, (s, pv) in enumerate(zip(slope, p)):
        has = ~np.isnan(values[row])
        fit = stats.linregress(YEARS[has], values[row, has], alternative="less")
        assert np.isclose(s, fit.slope)
        assert np.isclose(pv, fit.pvalue)


def test_percent_per_decade():
    assert np.isclose(percent_per_decade(np.log10(0.5)), -50)
    assert np.isclose(percent_per_decade(0), 0)


def test_mean_trend_matches_linregress_range():
    rng = np.random.default_rng(1)
    table = pd.DataFrame({
        "gid": np.repeat([1, 2, 3], len(YEARS)),
        "year": np.tile(YEARS, 3),
    })
    table["remainder"] = -0.02 * (table["year"] - 2015) + rng.normal(scale=0.05, size=len(table))
    trend, low, high = mean_trend(table)
    means = table.groupby("year")["remainder"].mean()
    fit = stats.linregress(means.index, means.values)
    margin = stats.t.ppf(0.975, len(means) - 2) * fit.stderr
    assert np.isclose(trend, 10 * fit.slope)
    assert np.isclose(low, 10 * (fit.slope - margin))
    assert np.isclose(high, 10 * (fit.slope + margin))


def test_site_trends_keeps_sites_with_enough_years():
    rows = []
    for gid, n_years in [(1, 10), (2, 8), (3, 7)]:
        for year in YEARS[:n_years]:
            rows.append({"gid": gid, "year": year, "remainder": -0.01 * (year - 2011)})
    trends = site_trends(pd.DataFrame(rows), min_years=8)
    assert list(trends["gid"]) == [1, 2]
    assert np.allclose(trends["slope"], -0.01)
    assert np.allclose(trends["sen_slope"], -0.01)
    assert np.allclose(trends["decade"], -0.1)
