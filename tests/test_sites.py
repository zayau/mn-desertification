import numpy as np
import pandas as pd
import shapely

from mn_desertification.sites import agrees_with_direction, assign_soums, outlines_around, pasture_type


def square(x0, y0, size):
    return shapely.box(x0, y0, x0 + size, y0 + size)


def test_small_soum_inside_a_larger_one_wins():
    outlines = {1: square(0, 0, 10), 2: square(4, 4, 2)}  # soum 2 sits inside soum 1, no hole
    sites = pd.DataFrame({"gid": [1, 2], "lon": [1.0, 5.0], "lat": [1.0, 5.0]})
    placed = assign_soums(sites, outlines)
    assert list(placed["soum_id"]) == [1, 2]
    assert list(placed["n_hits"]) == [1, 2]


def test_a_site_in_a_hole_is_outside_the_area():
    # Area 1 is a square drawn as two outlines: the outer edge and a hole in it.
    outlines = np.array([square(0, 0, 10), square(4, 4, 2), square(20, 0, 5)])
    area_of_outline = np.array([1, 1, 2])
    area_names = pd.Series({1: "winter-spring", 2: "summer-fall"})
    sites = pd.DataFrame({"gid": [1, 2, 3, 4], "lon": [1.0, 5.0, 22.0, 50.0], "lat": [1.0, 5.0, 2.0, 50.0]})
    counts = outlines_around(sites, outlines, area_of_outline)
    assert counts.loc[(2, 1)] == 2  # inside the outer edge and the hole
    pasture = pasture_type(sites["gid"], counts, area_names)
    assert list(pasture) == ["winter-spring", "outside map", "summer-fall", "outside map"]


def test_direction_check_agrees_with_the_odd_count_rule():
    sites = pd.DataFrame({"gid": [1, 2], "lon": [1.0, 5.0], "lat": [1.0, 5.0]})
    outer = shapely.box(0, 0, 10, 10, ccw=False)  # outer outlines run clockwise
    hole = shapely.box(4, 4, 6, 6, ccw=True)      # holes run counterclockwise
    assert agrees_with_direction(sites, np.array([outer, hole]), np.array([1, 1]))
    # Drawn clockwise, the inner square is a second outer outline, and the rules disagree
    second_outer = shapely.box(4, 4, 6, 6, ccw=False)
    assert not agrees_with_direction(sites, np.array([outer, second_outer]), np.array([1, 1]))
