import numpy as np
import pandas as pd

from mn_desertification.weather import fit_weather_model


def synthetic_sites(noise=0.0, seed=0):
    """Ten sites in each of two zones, with known rain and temperature effects."""
    rng = np.random.default_rng(seed)
    effects = {"Steppe zone": (1.2, -0.1), "Desert zone": (0.8, -0.15)}
    rows = []
    for zone, (b, c) in effects.items():
        for site in range(10):
            gid = len(rows) // 10 + 1
            site_level = rng.normal()
            for year in range(2011, 2021):
                rain = rng.uniform(100, 300)
                temp = rng.normal(18, 1.5)
                log_value = site_level + b * np.log10(rain) + c * temp + noise * rng.normal()
                rows.append({"gid": gid, "zone": zone, "year": year, "rain_growing": rain,
                             "temp_summer": temp, "value": 10 ** log_value})
    return pd.DataFrame(rows), effects


def test_fit_recovers_known_effects_without_noise():
    table, effects = synthetic_sites()
    fit = fit_weather_model(table, "value", with_temp=True)
    by_zone = fit.effects.set_index("zone")
    for zone, (b, c) in effects.items():
        assert np.isclose(by_zone.loc[zone, "b_rain"], b)
        assert np.isclose(by_zone.loc[zone, "c_temp"], c)
        assert np.isclose(by_zone.loc[zone, "R2"], 1)
    assert np.allclose(fit.remainders["remainder"], 0, atol=1e-10)


def test_remainders_average_to_zero_at_each_site():
    table, _ = synthetic_sites(noise=0.2, seed=1)
    fit = fit_weather_model(table, "value", with_temp=False)
    site_means = fit.remainders.groupby("gid")["remainder"].mean()
    assert np.allclose(site_means, 0, atol=1e-12)
    assert "c_temp" not in fit.effects.columns
