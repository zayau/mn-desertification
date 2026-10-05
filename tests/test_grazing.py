import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from mn_desertification.grazing import clustered_test, soum_responses


def test_soum_responses_trend_and_bump():
    rng = np.random.default_rng(5)
    rows = []
    for asid, slope in [(101, -0.03), (102, 0.0)]:
        for gid in range(2):
            for year in range(2011, 2021):
                # A little noise keeps each soum's scatter above zero, as in real data
                rows.append({"asid": asid, "gid": asid * 10 + gid, "year": year,
                             "remainder": slope * (year - 2011) + rng.normal(scale=1e-6)})
    responses = soum_responses(pd.DataFrame(rows), last_year=2020)
    assert np.isclose(responses.loc[101, "trend"], -0.3, atol=1e-4)
    assert np.isclose(responses.loc[102, "trend"], 0, atol=1e-4)
    # early mean (2011-2013) minus late mean (2016-2020) for a slope of -0.03 per year
    assert np.isclose(responses.loc[101, "bump"], -0.03 * (1 - 7), atol=1e-4)


def test_clustered_test_keeps_the_least_squares_estimate():
    rng = np.random.default_rng(4)
    data = pd.DataFrame({"x": rng.normal(size=60), "aimag": np.repeat(np.arange(12), 5)})
    data["y"] = 0.5 * data["x"] + rng.normal(scale=0.1, size=60)
    data.loc[3, "x"] = np.nan  # a missing value is dropped from the fit and the clusters
    result = clustered_test(data, "y ~ x", "x")
    plain = smf.ols("y ~ x", data=data).fit()
    assert result["n"] == 59
    assert result["clusters"] == 12
    assert np.isclose(result["estimate"], plain.params["x"])
    assert result["low"] < result["estimate"] < result["high"]
