import numpy as np
import pytest

# The Earth Engine library is an optional dependency. These tests need it to
# import the module, but none of them connects to Earth Engine.
pytest.importorskip("ee")

from mn_desertification.satellite import INDEX_FORMULAS, season_dates


def work_out(formula, red, nir):
    """An index formula worked out with plain numbers; its operators mean the same in Python."""
    return eval(formula, {"__builtins__": {}}, {"red": red, "nir": nir})


def test_ndvi_on_known_reflectances():
    red, nir = np.array([0.10, 0.20, 0.05]), np.array([0.40, 0.20, 0.45])
    assert np.allclose(work_out(INDEX_FORMULAS["ndvi"], red, nir), [0.6, 0.0, 0.8])


def test_msavi_is_the_soil_adjusted_index_that_sets_its_own_soil_term():
    red, nir = np.array([0.10, 0.20, 0.05]), np.array([0.40, 0.20, 0.45])
    msavi = work_out(INDEX_FORMULAS["msavi"], red, nir)
    # Worked by hand for the first pair: (1.8 - sqrt(1.8 ** 2 - 8 * 0.3)) / 2
    assert np.isclose(msavi[0], (1.8 - 0.84 ** 0.5) / 2)
    # The soil-adjusted index is (nir - red) * (1 + L) / (nir + red + L).
    # MSAVI is the value it takes when the soil term L is one minus the index.
    soil_term = 1 - msavi
    assert np.allclose(msavi, (nir - red) * (1 + soil_term) / (nir + red + soil_term))


def test_season_dates_end_the_day_after_the_last_day():
    assert season_dates(2015) == ("2015-07-01", "2015-09-01")
    assert season_dates(2016, (8, 1), (8, 31)) == ("2016-08-01", "2016-09-01")
    assert season_dates(2015, (6, 1), (9, 30)) == ("2015-06-01", "2015-10-01")
