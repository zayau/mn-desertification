"""What the method can detect, and whether the results depend on the choices made.

Three tools, after Wessels et al. (2012), section 2.5:

- The detection test plants declines of known size into data whose year order
  has been shuffled, and counts how often the trend test finds them.
- The permutation test shuffles the order of the years for all sites together,
  and asks how often a shuffled order gives as many declining sites as the
  real one.
- The robustness check reruns the weather model and both tests with one
  analytical choice changed.

Shuffling keeps the year-to-year noise and destroys any trend. The random
numbers are drawn in a fixed order, so a given seed gives the same results.
"""

import numpy as np
import pandas as pd

from .quality import floored_log
from .rules import ALPHA, FLOOR, MIN_YEARS
from .trends import trend_test


def shuffle_within_zones(values: np.ndarray, zones: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """A copy of ``values`` (sites × years) with the years in a new random order.

    Each zone gets one new order, shared by all its sites, so that years that
    were good or bad across a zone stay together. Zones are taken in sorted
    order.
    """
    shuffled = values.copy()
    for zone in np.unique(zones):
        rows = zones == zone
        shuffled[rows] = shuffled[rows][:, rng.permutation(values.shape[1])]
    return shuffled


def planted_decline(size: float, start: int, years: np.ndarray) -> np.ndarray:
    """log10 change in each year for a decline that starts in ``start``.

    The decline grows in a straight line from zero in ``start`` to its full
    ``size`` (a fraction, so 0.2 is 20%) in the last year.
    """
    share = np.clip((years - start) / (years[-1] - start), 0, 1)
    return np.log10(1 - size) * share


def detection_shares(values: np.ndarray, years: np.ndarray, soums: np.ndarray, zones: np.ndarray,
                     min_years: int = MIN_YEARS) -> dict:
    """Share of sites, soums and zones whose series shows a significant decline.

    Sites need ``min_years`` years. Soums and zones are tested on the mean of
    their sites in each year, and also need ``min_years`` years.
    """
    n_years = (~np.isnan(values)).sum(axis=1)
    _, p_site = trend_test(values[n_years >= min_years], years)
    shares = {"site": (p_site < ALPHA).mean()}
    table = pd.DataFrame(values)
    for level, groups in [("soum", soums), ("zone", zones)]:
        means = table.groupby(groups).mean()
        means = means[means.notna().sum(axis=1) >= min_years]
        _, p = trend_test(means.to_numpy(), years)
        shares[level] = (p < ALPHA).mean()
    return shares


def detection_test(grids: dict, soums: np.ndarray, zones: np.ndarray, sizes=(0, 0.1, 0.2, 0.3, 0.4),
                   starts=(2012, 2014, 2016), n_shuffles: int = 50, seed: int = 7) -> pd.DataFrame:
    """The detection test for each weather model.

    ``grids`` maps a model name to its sites × years table of remainders, with
    the same sites in the same order as ``soums`` and ``zones``. For each of
    ``n_shuffles`` shuffles within zones, every size of decline is planted with
    every start year (size 0, no decline, once), and the share of sites, soums
    and zones flagged is recorded. With size 0 that share is the false alarm
    rate.

    Returns one row per model, shuffle, size, start and level.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for model, grid in grids.items():
        years = grid.columns.to_numpy()
        for shuffle in range(n_shuffles):
            base = shuffle_within_zones(grid.to_numpy(), zones, rng)
            for size in sizes:
                for start in (starts if size > 0 else [None]):
                    values = base if size == 0 else base + planted_decline(size, start, years)
                    for level, share in detection_shares(values, years, soums, zones).items():
                        rows.append({"model": model, "shuffle": shuffle, "size": size, "start": start,
                                     "level": level, "share": share})
    return pd.DataFrame(rows)


def permutation_test(grid: pd.DataFrame, rng: np.random.Generator, n_permutations: int = 1000,
                     min_years: int = MIN_YEARS):
    """How unusual the real order of years is.

    Shuffles the order of the years ``n_permutations`` times, with one order
    for all sites together, so that the country's good and bad years stay as
    they were and only their order changes. Returns the real share of sites
    with a significant decline and the array of shuffled shares. The count of
    shuffled shares at least as large as the real one, divided by
    ``n_permutations``, is a one-sided p-value.
    """
    years = grid.columns.to_numpy()
    values = grid.to_numpy()
    enough = grid.notna().sum(axis=1).to_numpy() >= min_years
    _, p = trend_test(values[enough], years)
    real_share = (p < ALPHA).mean()
    shuffled_shares = []
    for _ in range(n_permutations):
        order = rng.permutation(len(years))
        _, p_shuffled = trend_test(values[:, order][enough], years)
        shuffled_shares.append((p_shuffled < ALPHA).mean())
    return real_share, np.array(shuffled_shares)


def robustness_grid(site_year: pd.DataFrame, flagged: set, first_year: int = 2011, last_year: int = 2020,
                    floor: float = FLOOR, keep_flagged: bool = False, drop_above: float | None = None,
                    with_temp: bool = False):
    """The weather model's remainders with one analytical choice changed.

    ``site_year`` needs ``gid``, ``year``, ``asid``, ``zone``, ``bms``,
    ``rain_growing`` and ``temp_summer``; ``flagged`` is a set of (site, year)
    pairs. Returns the remainders as a sites × years table, and each site's
    soum and zone in the same order.
    """
    d = site_year[site_year["year"].between(first_year, last_year)].copy()
    if not keep_flagged:
        d = d[[(gid, year) not in flagged for gid, year in zip(d["gid"], d["year"])]]
    if drop_above is not None:
        d = d[d["bms"] <= drop_above]

    d["y"] = floored_log(d["bms"], floor)
    d["rain"] = np.log10(d["rain_growing"])
    columns = ["y", "rain"] + (["temp_summer"] if with_temp else [])
    for column in columns:  # each site against its own average
        d[column] = d[column] - d.groupby("gid")[column].transform("mean")
    for _, group in d.groupby("zone", observed=True):  # the weather effect, zone by zone
        X = group[columns[1:]].to_numpy()
        coef, *_ = np.linalg.lstsq(X, group["y"].to_numpy(), rcond=None)
        d.loc[group.index, "remainder"] = group["y"].to_numpy() - X @ coef

    grid = d.pivot(index="gid", columns="year", values="remainder")
    info = d.drop_duplicates("gid").set_index("gid").loc[grid.index]
    return grid, info["asid"].to_numpy(), info["zone"].to_numpy()


def robustness_summary(grid: pd.DataFrame, soums: np.ndarray, zones: np.ndarray, min_years: int,
                       starts, rng: np.random.Generator) -> dict:
    """The main numbers of the analysis for one choice of data and model.

    - the national trend, the slope of the all-site yearly mean, per decade;
    - the share of sites with a significant decline;
    - how many of 1,000 shuffled year orders reach that share;
    - how often a planted 20% decline is found at sites, soums and zones,
      averaged over 50 shuffles within zones and the given start years.

    The random numbers are drawn in that order, so passing a fresh generator
    with the same seed gives the same result for every choice. Values are not
    rounded; round them for display.
    """
    years = grid.columns.to_numpy()
    values = grid.to_numpy()
    national = 10 * np.polyfit(years, np.nanmean(values, axis=0), 1)[0]

    real_share, shuffled_shares = permutation_test(grid, rng, min_years=min_years)

    found = {"site": [], "soum": [], "zone": []}
    for _ in range(50):
        base = shuffle_within_zones(values, zones, rng)
        for start in starts:
            shares = detection_shares(base + planted_decline(0.2, start, years), years, soums, zones, min_years)
            for level, share in shares.items():
                found[level].append(share)

    return {
        "national per decade": national,
        "sites declining": real_share,
        "shuffles reaching it": int((shuffled_shares >= real_share).sum()),
        "20% found: site": np.mean(found["site"]),
        "20% found: soum": np.mean(found["soum"]),
        "20% found: zone": np.mean(found["zone"]),
    }
