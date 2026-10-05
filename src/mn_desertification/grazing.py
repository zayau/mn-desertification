"""Herd measures, soum-level responses and the regressions of the grazing analysis.

Herds are counted per soum, so the biomass and greenness responses are
computed per soum too, from the mean of each soum's sites in each year.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .trends import trend_test


def soum_responses(remainders: pd.DataFrame, last_year: int, early=(2011, 2013), late_start: int = 2016) -> pd.DataFrame:
    """Each soum's trend and post-dzud bump in a series of remainders.

    Sites are averaged by soum and year. Soums missing more than two years are
    left out. Returns one row per soum (``asid``) with:

    - ``trend``: the least-squares slope of the soum's yearly means, in log10
      per decade;
    - ``bump``: the mean of the ``early`` years minus the mean of the years
      from ``late_start`` to ``last_year``.
    """
    grid = remainders.groupby(["asid", "year"])["remainder"].mean().unstack()
    grid = grid[grid.notna().sum(axis=1) >= grid.shape[1] - 2]
    slope, _ = trend_test(grid.to_numpy(), grid.columns.to_numpy())
    early_mean = grid.loc[:, early[0]:early[1]].mean(axis=1)
    late_mean = grid.loc[:, late_start:last_year].mean(axis=1)
    return pd.DataFrame({"trend": 10 * slope, "bump": early_mean - late_mean}, index=grid.index)


def soum_table(biomass: pd.DataFrame, greenness: pd.DataFrame, herd: pd.DataFrame, soum_zone: pd.Series,
               last_year: int) -> pd.DataFrame:
    """One row per soum with its responses, herd measures, zone and aimag.

    ``herd`` comes from ``data.read_herd_before_summer``. The herd measures:

    - ``dzud_loss``: log10 of the herd before summer 2010 over the herd before
      summer 2011, that is December 2009 against December 2010. Positive where
      animals were lost.
    - ``herd_growth``: log10 of the herd before ``last_year``'s summer over the
      herd before summer 2011.

    The aimag code is the soum code without its last two digits.
    """
    table = soum_responses(biomass, last_year).add_prefix("bio_")
    table = table.join(soum_responses(greenness, last_year).add_prefix("green_"), how="outer")
    table["dzud_loss"] = np.log10(herd[2010] / herd[2011])
    table["herd_growth"] = np.log10(herd[last_year] / herd[2011])
    table["zone"] = soum_zone
    table["aimag"] = table.index // 100
    return table


def clustered_test(data: pd.DataFrame, formula: str, term: str, cluster: str = "aimag") -> dict:
    """Fit ``formula`` by least squares and report one coefficient.

    Standard errors are clustered by ``cluster``: units in the same aimag share
    weather, herders who move between them and perhaps a survey team, so they
    are not independent. statsmodels drops rows missing any variable in the
    formula; the fit is repeated on exactly those rows so that the clusters
    line up with them.

    Returns the estimate, its 95% range, the two-sided p-value, the number of
    rows used and the number of clusters.
    """
    used = data.loc[smf.ols(formula, data=data).data.row_labels]
    model = smf.ols(formula, data=used).fit(cov_type="cluster", cov_kwds={"groups": used[cluster]})
    low, high = model.conf_int().loc[term]
    return {"n": int(model.nobs), "clusters": used[cluster].nunique(), "estimate": model.params[term],
            "low": low, "high": high, "p": model.pvalues[term]}
