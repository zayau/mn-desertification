import numpy as np
import pandas as pd

from mn_desertification.greenness import add_clear_share, clearest_per_day, in_season, long_record_start, read_landsat


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
