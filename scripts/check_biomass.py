"""First look at the ground biomass in the Purevjav et al. 2025 release.

Reads bms_plot.dta (August biomass by site and year) and vegi_plot_modis_aug.dta
(August MODIS indices for the same sites) and prints the numbers recorded in
docs/data-checks.md. Needs pandas.

    python3 scripts/check_biomass.py [path/to/tables]
"""
import sys

import numpy as np
import pandas as pd

DEFAULT = "data/raw/namem/tables"


def corr(x, y):
    ok = x.notna() & y.notna()
    return np.corrcoef(x[ok], y[ok])[0, 1]


def main(folder):
    b = pd.read_stata(f"{folder}/bms_plot.dta")
    v = pd.read_stata(f"{folder}/vegi_plot_modis_aug.dta")

    per_site = b.groupby("gid")["year"].nunique()
    print(f"records {len(b)}, sites {b.gid.nunique()}, years {b.year.min()}-{b.year.max()}")
    print(f"sites with 12 or more years {int((per_site >= 12).sum())}, with all 14 years {int((per_site == 14).sum())}")
    print(f"biomass c/ha: median {b.bms.median():.2f}, mean {b.bms.mean():.2f}, "
          f"below 0.1 {int((b.bms < 0.1).sum())}, above 30 {int((b.bms > 30).sum())}")

    m = b.merge(v, on=["gid", "year"])
    m["lb"] = np.log(m["bms"])
    means = m.groupby("gid")[["lb", "ndvi_sm_ave"]].mean()
    within = m[["lb", "ndvi_sm_ave"]] - m.groupby("gid")[["lb", "ndvi_sm_ave"]].transform("mean")
    years = m.groupby("year")[["bms", "ndvi_sm_ave"]].mean()
    print(f"log biomass vs August NDVI: across sites r {corr(means.lb, means.ndvi_sm_ave):.2f}, "
          f"within sites across years r {corr(within.lb, within.ndvi_sm_ave):.2f}, "
          f"national yearly means r {corr(years.bms, years.ndvi_sm_ave):.2f}")

    b["lb"] = np.log(b["bms"])
    total = b["lb"].var()
    site = b.groupby("gid")["lb"].transform("mean")
    year = b.groupby("year")["lb"].transform("mean") - b["lb"].mean()
    print(f"variance of log biomass explained: site means {1 - (b.lb - site).var() / total:.2f}, "
          f"site means and national year effects {1 - (b.lb - site - year).var() / total:.2f}")

    b["anom"] = b["lb"] - site - year
    b = b.sort_values(["gid", "year"])
    prev = b.groupby("gid")["anom"].shift(1)
    consecutive = b.groupby("gid")["year"].diff() == 1
    print(f"site anomaly vs previous year's: r {corr(b.anom[consecutive], prev[consecutive]):.2f} "
          f"(n {int(consecutive.sum())})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
