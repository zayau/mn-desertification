"""A model of clipped biomass from satellite signals, weather and herds, tested on years it has not seen.

The predictors are added in rungs (``RUNGS``), each on top of the one before,
and two kinds of model are fitted at every rung: a straight line, zone by
zone, and boosted trees. docs/design.md gives the rules under "The biomass
model (step 3)". The boosted trees need the optional ``model`` dependencies.
"""

import numpy as np
import pandas as pd

from .greenness import BANDS, INDICES, season_medians
from .rules import ZONES

# The ten satellite signals of one season: six bands and four indices.
SIGNALS = BANDS + INDICES

# The ladder of predictors. A model at a rung uses that rung and every rung above it.
RUNGS = {
    "1 weather": ["log_rain", "temp_summer"],
    "2 greenness": ["log_ndvi"],
    "3 all bands": BANDS + ["msavi", "nir_swir1", "swir1_swir2"],
    "4 the season": [f"{signal}_{when}" for when in ("june", "september", "before") for signal in SIGNALS],
    "5 herds": ["log_herd"],
}


def predictors_up_to(rung: str) -> list[str]:
    """The predictors of ``rung`` and of every rung before it."""
    names = []
    for name, predictors in RUNGS.items():
        names += predictors
        if name == rung:
            return names
    raise KeyError(rung)


def landsat_predictors(observations: pd.DataFrame) -> pd.DataFrame:
    """The Landsat predictors of every site-year.

    ``observations`` are the ones that count, on the Landsat 7 scale and with
    their indices (``greenness.counting`` and ``greenness.with_indices``).
    Returns one row per site and year with the median of each signal in July
    and August, under the signal's own name; in June and in September, ending
    in ``_june`` and ``_september``; and in the July and August of the year
    before, ending in ``_before``. ``log_ndvi`` is the log10 of the July and
    August NDVI. A season with no observation leaves its columns empty.
    """
    def medians(first, last, ending):
        table = season_medians(observations, SIGNALS, first, last).drop(columns="n_observations")
        return table.rename(columns={signal: signal + ending for signal in SIGNALS})

    summer = medians((7, 1), (8, 31), "")
    before = summer.assign(year=summer["year"] + 1).rename(columns={signal: signal + "_before" for signal in SIGNALS})
    table = summer
    for other in [medians((6, 1), (6, 30), "_june"), medians((9, 1), (9, 30), "_september"), before]:
        table = table.merge(other, on=["gid", "year"], how="outer")
    table["log_ndvi"] = np.log10(table["ndvi"].where(table["ndvi"] > 0))
    return table


def estimate_unseen(fit_rows: pd.DataFrame, new_rows: pd.DataFrame, predictors: list[str], kind: str,
                    target: str = "log_bms") -> pd.DataFrame:
    """Fit a model to some site-years and estimate others it has not seen.

    Everything enters as a site's departure from its own average, and that
    average is taken over ``fit_rows`` only, so nothing of ``new_rows`` leaks
    into the fit. ``kind`` is ``"line"`` for a straight-line model fitted zone
    by zone with no intercept, as in the weather model, or ``"trees"`` for
    boosted trees with the zone as a predictor. Where a predictor is missing,
    the line takes the site's average and the trees take it as missing.

    Returns the rows of ``new_rows`` whose site is in ``fit_rows``, with
    ``departure`` (the target against the site's average), ``estimate`` (the
    model's estimate of it) and ``remainder`` (the first minus the second).
    """
    columns = [target, *predictors]
    averages = fit_rows.groupby("gid")[columns].mean()
    fit = fit_rows[columns] - averages.reindex(fit_rows["gid"]).to_numpy()
    new = new_rows[columns] - averages.reindex(new_rows["gid"]).to_numpy()
    known = new[target].notna().to_numpy()   # sites that have an average to depart from
    new_rows, new = new_rows[known], new[known]

    if kind == "line":
        estimate = pd.Series(np.nan, index=new_rows.index)
        for zone in fit_rows["zone"].unique():
            in_fit, in_new = (fit_rows["zone"] == zone).to_numpy(), (new_rows["zone"] == zone).to_numpy()
            slopes, *_ = np.linalg.lstsq(fit.loc[in_fit, predictors].fillna(0).to_numpy(), fit.loc[in_fit, target].to_numpy(), rcond=None)
            estimate[in_new] = new.loc[in_new, predictors].fillna(0).to_numpy() @ slopes
    elif kind == "trees":
        from sklearn.ensemble import HistGradientBoostingRegressor

        def with_zone(departures, rows):
            return np.column_stack([departures[predictors].to_numpy(), pd.Categorical(rows["zone"], categories=ZONES).codes])

        trees = HistGradientBoostingRegressor(random_state=0, categorical_features=[len(predictors)])
        trees.fit(with_zone(fit, fit_rows), fit[target].to_numpy())
        estimate = pd.Series(trees.predict(with_zone(new, new_rows)), index=new_rows.index)
    else:
        raise ValueError(f"kind must be 'line' or 'trees', not {kind!r}")

    result = new_rows[["gid", "year", "zone"]].copy()
    result["departure"] = new[target]
    result["estimate"] = estimate
    result["remainder"] = result["departure"] - result["estimate"]
    return result


def leave_year_out(table: pd.DataFrame, predictors: list[str], kind: str, target: str = "log_bms") -> pd.DataFrame:
    """Estimate every year with a model fitted to the other years.

    Returns the rows of ``estimate_unseen`` for every year in turn. The
    ``remainder`` of a year is what the model, never having seen that year,
    leaves unexplained in it.
    """
    years = sorted(table["year"].unique())
    return pd.concat([estimate_unseen(table[table["year"] != year], table[table["year"] == year], predictors, kind, target)
                      for year in years], ignore_index=True)


def forward(table: pd.DataFrame, predictors: list[str], kind: str, last_fit_year: int, target: str = "log_bms") -> pd.DataFrame:
    """Fit a model to the years up to ``last_fit_year`` and estimate the years after."""
    early = table["year"] <= last_fit_year
    return estimate_unseen(table[early], table[~early], predictors, kind, target)


def skill(result: pd.DataFrame) -> float:
    """The share of the sites' departures from their averages that the estimates explain.

    Zero is what a model scores that always estimates the site's average, and
    a model can score below zero.
    """
    return float(1 - (result["remainder"] ** 2).sum() / (result["departure"] ** 2).sum())
