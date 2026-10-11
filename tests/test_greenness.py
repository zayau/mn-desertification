import numpy as np
import pandas as pd

from mn_desertification.greenness import (add_clear_share, clearest_per_day, fit_conversion, in_season,
                                          long_record_start, read_landsat, sensor_pairs, with_indices)
from mn_desertification.rules import TO_LANDSAT7


def observation(**changes):
    row = {"sensor": "landsat8", "gid": 1, "radius_m": 100, "overpass": "133_2015-07-11_48",
           "time": pd.Timestamp("2015-07-11 03:52:50"), "red": 0.1, "nir": 0.3, "clear_pixels": 30.0}
    return row | changes


def test_clear_share_is_the_clear_part_of_the_whole_circle():
    whole = np.pi * 100 ** 2 / 30 ** 2   # pixels in a circle of 100 m
    table = add_clear_share(pd.DataFrame([observation(clear_pixels=whole), observation(clear_pixels=whole / 4),
                                          observation(radius_m=50, clear_pixels=whole / 4)]))
    assert np.allclose(table["clear_share"], [1, 0.25, 1])


def test_clearest_per_day_keeps_one_row_for_a_site_seen_twice_in_one_pass():
    table = pd.DataFrame([
        observation(overpass="142_2015-06-24_46", time=pd.Timestamp("2015-06-24 04:46:40"), clear_pixels=20.0),
        observation(overpass="142_2015-06-24_45", time=pd.Timestamp("2015-06-24 04:48:16"), clear_pixels=34.0),
        observation(overpass="142_2015-07-10_46", time=pd.Timestamp("2015-07-10 04:46:51")),   # another day
        observation(sensor="landsat7", time=pd.Timestamp("2015-06-24 04:40:00")),               # another sensor
        observation(radius_m=50, time=pd.Timestamp("2015-06-24 04:46:40"), clear_pixels=8.0),   # another circle
    ])
    kept = clearest_per_day(table)
    assert len(kept) == 4
    same_day = kept[(kept["sensor"] == "landsat8") & (kept["radius_m"] == 100) & (kept["time"].dt.day == 24)]
    assert same_day["overpass"].to_list() == ["142_2015-06-24_45"]


def test_in_season_includes_both_end_days():
    days = ["2015-06-30", "2015-07-01", "2015-08-31", "2015-09-01", "2016-07-15"]
    table = pd.DataFrame([observation(time=pd.Timestamp(day + " 04:00:00")) for day in days])
    kept = in_season(table)
    assert kept["time"].dt.strftime("%Y-%m-%d").to_list() == ["2015-07-01", "2015-08-31", "2016-07-15"]
    assert kept["year"].to_list() == [2015, 2015, 2016]
    assert len(in_season(table, (8, 1), (8, 31))) == 1


def test_long_record_starts_after_the_last_year_that_falls_short():
    counts = pd.Series({1986: 800, 1987: 1200, 1988: 900, 1989: 1300, 1990: 1250, 1992: 1400})
    # 1991 is left out, so it has no site, and the record can only start in 1992
    assert long_record_start(counts, needed=1000) == 1992
    assert long_record_start(counts.drop(1992), needed=1000) == 1989
    assert long_record_start(counts.drop(1992), needed=700) == 1986
    assert long_record_start(counts.drop(1992), needed=1300) is None


def test_read_landsat_reads_times_with_and_without_fractions(tmp_path):
    (tmp_path / "landsat5_1989.csv").write_text(
        "sensor,gid,radius_m,overpass,time,red,nir,ndvi,msavi,clear_pixels\n"
        "landsat5,1,100,131_1989-07-17_48,1989-07-17 03:33:02,0.1,0.3,0.5,0.3,34.5\n"
        "landsat5,2,100,131_1989-07-17_48,1989-07-17 03:33:26.500,0.1,0.3,0.5,0.3,34.5\n")
    (tmp_path / "landsat5_1984.csv").write_text("sensor,gid,radius_m,overpass,time,red,nir,ndvi,msavi,clear_pixels\n")
    table = read_landsat(tmp_path)
    assert len(table) == 2
    assert table["time"].dt.second.to_list() == [2, 26]


def test_with_indices_converts_the_newer_sensors_only_and_keeps_the_pixel_means():
    table = pd.DataFrame([observation(sensor="landsat7", ndvi=0.48, msavi=0.3),
                          observation(sensor="landsat8", ndvi=0.48, msavi=0.3)])
    measured = with_indices(table, to_landsat7=False)
    assert np.allclose(measured["ndvi"], (0.3 - 0.1) / (0.3 + 0.1))
    assert measured["ndvi_pixels"].to_list() == [0.48, 0.48]

    converted = with_indices(table)
    red8 = TO_LANDSAT7["red"][0] + TO_LANDSAT7["red"][1] * 0.1
    nir8 = TO_LANDSAT7["nir"][0] + TO_LANDSAT7["nir"][1] * 0.3
    assert np.allclose(converted["red"], [0.1, red8]) and np.allclose(converted["nir"], [0.3, nir8])
    assert np.allclose(converted["ndvi"], [0.5, (nir8 - red8) / (nir8 + red8)])
    assert converted["ndvi_pixels"].to_list() == [0.48, 0.48]


def test_sensor_pairs_keeps_observations_of_one_site_within_the_days_allowed():
    table = with_indices(pd.DataFrame([
        observation(sensor="landsat7", time=pd.Timestamp("2015-07-03 03:50:00"), ndvi=0.5, msavi=0.3),
        observation(sensor="landsat8", time=pd.Timestamp("2015-07-11 03:52:50"), ndvi=0.5, msavi=0.3),   # 8 days later
        observation(sensor="landsat8", time=pd.Timestamp("2015-07-02 03:58:00"), ndvi=0.5, msavi=0.3),   # 1 day earlier
        observation(sensor="landsat8", time=pd.Timestamp("2015-07-27 03:52:00"), ndvi=0.5, msavi=0.3),   # too late
        observation(sensor="landsat8", gid=2, time=pd.Timestamp("2015-07-04 03:52:00"), ndvi=0.5, msavi=0.3),  # another site
    ]))
    pairs = sensor_pairs(table, "landsat7", "landsat8")
    assert sorted(pairs["days_apart"]) == [-1, 8]
    assert {"red_first", "red_second", "ndvi_first", "ndvi_second"} <= set(pairs.columns)
    assert len(sensor_pairs(table, "landsat7", "landsat8", days=1)) == 1


def test_fit_conversion_recovers_a_known_line_and_with_indices_applies_it():
    rng = np.random.default_rng(3)
    true_red, true_nir = rng.uniform(0.05, 0.3, 400), rng.uniform(0.15, 0.45, 400)
    # The second sensor reads red 0.01 low and near infrared 5% high; both have a little noise
    pairs = pd.DataFrame({
        "red_first": true_red + rng.normal(scale=0.002, size=400),
        "red_second": true_red - 0.01 + rng.normal(scale=0.002, size=400),
        "nir_first": true_nir + rng.normal(scale=0.002, size=400),
        "nir_second": true_nir * 1.05 + rng.normal(scale=0.002, size=400),
    })
    lines = fit_conversion(pairs)
    assert np.isclose(lines["red"][0], 0.01, atol=0.002) and np.isclose(lines["red"][1], 1, atol=0.02)
    assert np.isclose(lines["nir"][0], 0, atol=0.006) and np.isclose(lines["nir"][1], 1 / 1.05, atol=0.02)
    # The other way round, the first sensor is put on the second's scale
    back = fit_conversion(pairs, onto="second")
    assert np.isclose(back["red"][0], -0.01, atol=0.002)

    table = pd.DataFrame([observation(sensor="landsat7", ndvi=0.5, msavi=0.3), observation(sensor="landsat8", ndvi=0.5, msavi=0.3)])
    converted = with_indices(table, conversions={"landsat8": {"red": (0.01, 1.0), "nir": (0.0, 0.9)}})
    assert np.allclose(converted["red"], [0.1, 0.11]) and np.allclose(converted["nir"], [0.3, 0.27])
