import numpy as np
import pandas as pd
import pytest

from mn_desertification import trends
from mn_desertification.model import (RUNGS, estimate_unseen, forward, landsat_predictors, leave_group_out, leave_year_out,
                                      level_skill, predictors_up_to, skill)


def declining_table(seed=1):
    """Sites whose biomass falls by 0.02 log10 a year. One signal follows the fall, the other is noise."""
    rng = np.random.default_rng(seed)
    rows = []
    for gid in range(60):
        level = rng.normal()
        for year in range(2011, 2021):
            fall = -0.02 * (year - 2011) + rng.normal(scale=0.05)
            rows.append({"gid": gid, "year": year, "zone": "Steppe zone" if gid % 2 else "Desert zone",
                         "log_bms": level + fall + rng.normal(scale=0.02),
                         "sees_it": 2 * fall + rng.normal(scale=0.01), "noise": rng.normal()})
    return pd.DataFrame(rows)


def test_predictors_add_up_rung_by_rung():
    assert predictors_up_to("1 weather") == ["log_rain", "temp_summer"]
    assert predictors_up_to("2 greenness") == ["log_rain", "temp_summer", "log_ndvi"]
    assert len(predictors_up_to("5 herds")) == sum(len(names) for names in RUNGS.values())


def test_a_signal_that_follows_the_fall_removes_the_trend_and_noise_does_not():
    table = declining_table()
    seen = leave_year_out(table, ["sees_it"], "line")
    blind = leave_year_out(table, ["noise"], "line")
    assert len(seen) == len(table)
    # With the year's own value left out of the site's average, a fall of 0.2 per decade shows as 0.2 * 10 / 9
    assert np.isclose(trends.mean_trend(blind)[0], -0.2 * 10 / 9, atol=0.03)
    assert abs(trends.mean_trend(seen)[0]) < 0.03
    assert skill(seen) > 0.8 and skill(blind) < 0.05


def test_forward_fits_the_early_years_and_estimates_the_later_ones():
    table = declining_table()
    result = forward(table, ["sees_it"], "line", last_fit_year=2015)
    assert sorted(result["year"].unique()) == [2016, 2017, 2018, 2019, 2020]
    assert abs(result["remainder"].mean()) < 0.03
    assert forward(table, ["noise"], "line", last_fit_year=2015)["remainder"].mean() < -0.08


def test_a_missing_predictor_counts_as_the_sites_average_for_the_line():
    table = declining_table()
    holed = table.copy()
    holed.loc[holed.index[::7], "sees_it"] = np.nan
    result = estimate_unseen(holed[holed["year"] < 2020], holed[holed["year"] == 2020], ["sees_it"], "line")
    assert result["estimate"].notna().all()
    assert (result.loc[holed.loc[result.index, "sees_it"].isna().to_numpy(), "estimate"] == 0).all()


def test_trees_also_follow_the_signal():
    pytest.importorskip("sklearn")
    table = declining_table()
    seen = leave_year_out(table, ["sees_it", "noise"], "trees")
    assert skill(seen) > 0.6
    assert abs(trends.mean_trend(seen)[0]) < 0.08


def test_landsat_predictors_cover_the_four_seasons():
    days = {"2014-07-20": 0.20, "2015-06-10": 0.10, "2015-07-05": 0.30, "2015-08-20": 0.50, "2015-09-12": 0.25}
    rows = [{"gid": 1, "time": pd.Timestamp(day + " 04:00:00"), **{signal: value for signal in
             ["blue", "green", "red", "nir", "swir1", "swir2", "ndvi", "msavi", "nir_swir1", "swir1_swir2"]}}
            for day, value in days.items()]
    table = landsat_predictors(pd.DataFrame(rows)).set_index("year")
    assert np.isclose(table.loc[2015, "ndvi"], 0.40) and np.isclose(table.loc[2015, "ndvi_june"], 0.10)
    assert np.isclose(table.loc[2015, "ndvi_september"], 0.25) and np.isclose(table.loc[2015, "ndvi_before"], 0.20)
    assert np.isclose(table.loc[2015, "log_ndvi"], np.log10(0.40))
    assert np.isnan(table.loc[2014, "ndvi_june"])


def test_leave_group_out_places_sites_it_has_never_seen():
    rng = np.random.default_rng(4)
    rows = []
    for gid in range(80):
        greenness = rng.uniform(0.1, 0.6)
        for year in range(2011, 2016):
            rows.append({"gid": gid, "year": year, "aimag": gid % 8, "zone": "Steppe zone" if gid % 2 else "Desert zone",
                         "green": greenness + rng.normal(scale=0.02), "noise": rng.normal(),
                         "log_bms": 2 * greenness + rng.normal(scale=0.05)})
    table = pd.DataFrame(rows)
    table.loc[table.index[::9], "green"] = np.nan   # a missing value takes the zone's average
    placed = leave_group_out(table, ["green"], "line")
    lost = leave_group_out(table, ["noise"], "line")
    assert len(placed) == len(table) and placed["estimate"].notna().all()
    assert level_skill(placed) > 0.75 and level_skill(placed, by_site=True) > level_skill(placed)
    assert level_skill(lost) < 0.05
