import numpy as np
import pandas as pd

from mn_desertification.quality import drop_flagged, flag_recording_errors, floored_log


def test_floored_log_raises_values_below_the_floor():
    logs = floored_log(pd.Series([0.01, 0.1, 1.0, 10.0]))
    assert np.allclose(logs, [-1, -1, 0, 1])


def test_flags_a_lone_spike_and_a_value_off_the_scale():
    # Twenty sites in one zone, two soums, all at 1 c/ha in normal rain, except:
    # site 1 at 20 c/ha in 2015, alone in its soum   -> lone spike
    # site 11 at 15 c/ha in 2016, in a wet year      -> not flagged
    # site 5 at 50 c/ha in 2018, over twice 20       -> off the scale
    rows = []
    for gid in range(1, 21):
        for year in range(2011, 2021):
            rows.append({"gid": gid, "year": year, "asid": 1 if gid <= 10 else 2,
                         "zone": "Steppe zone", "bms": 1.0, "rain_pct": 100.0})
    site_year = pd.DataFrame(rows)
    site_year.loc[(site_year["gid"] == 1) & (site_year["year"] == 2015), "bms"] = 20
    site_year.loc[(site_year["gid"] == 11) & (site_year["year"] == 2016), ["bms", "rain_pct"]] = [15, 130]
    site_year.loc[(site_year["gid"] == 5) & (site_year["year"] == 2018), "bms"] = 50

    flags = flag_recording_errors(site_year).sort_values("gid")
    assert list(zip(flags["gid"], flags["year"], flags["flag"])) == [
        (1, 2015, "lone spike"),
        (5, 2018, "off the scale"),
    ]
    assert len(drop_flagged(site_year, flags)) == len(site_year) - 2
