import numpy as np
import pandas as pd

from mn_desertification.detection import (
    detection_shares,
    permutation_test,
    planted_decline,
    shuffle_within_zones,
)

YEARS = np.arange(2011, 2021)


def test_planted_decline_grows_from_start_to_full_size():
    decline = planted_decline(0.2, 2014, YEARS)
    assert np.allclose(decline[YEARS <= 2014], 0)
    assert np.isclose(decline[-1], np.log10(0.8))
    assert np.all(np.diff(decline[YEARS >= 2014]) < 0)


def test_shuffle_keeps_each_row_and_shares_the_order_within_a_zone():
    values = np.tile(YEARS.astype(float), (4, 1)) + np.arange(4)[:, None] * 100
    zones = np.array(["a", "a", "b", "b"])
    shuffled = shuffle_within_zones(values, zones, np.random.default_rng(0))
    for row in range(4):
        assert sorted(shuffled[row]) == sorted(values[row])
    assert np.array_equal(shuffled[0] - values[0, 0], shuffled[1] - values[1, 0])
    assert np.array_equal(shuffled[2] - values[2, 0], shuffled[3] - values[3, 0])


def test_detection_shares_find_a_steep_decline():
    rng = np.random.default_rng(2)
    values = rng.normal(scale=0.01, size=(30, len(YEARS))) - 0.05 * (YEARS - 2011)
    soums = np.repeat(np.arange(10), 3)
    zones = np.repeat(np.array(["a", "b", "c"]), 10)
    shares = detection_shares(values, YEARS, soums, zones)
    assert shares == {"site": 1.0, "soum": 1.0, "zone": 1.0}


def test_permutation_test_is_reproducible_with_a_seed():
    rng = np.random.default_rng(3)
    grid = pd.DataFrame(rng.normal(size=(50, len(YEARS))), columns=YEARS)
    first = permutation_test(grid, np.random.default_rng(11), n_permutations=50)
    second = permutation_test(grid, np.random.default_rng(11), n_permutations=50)
    assert first[0] == second[0]
    assert np.array_equal(first[1], second[1])
