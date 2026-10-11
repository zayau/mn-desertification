"""Extract Landsat reflectance at the monitoring sites, overpass by overpass.

For every Landsat overpass from June to September, and every site it covers,
this saves what the overpass shows within 100 m and within 50 m of the plot.
The table of ``satellite.landsat_observations`` is written to
``data/processed/landsat/``, one file per sensor and year.

The whole record takes about an hour and about 100 hours of Earth Engine's
compute allowance. A sensor-year that already has a file is skipped,
so the script can be stopped and started again, and a failed sensor-year is
tried again on the next run.

Run from the repository root:

    .venv/bin/python scripts/extract_landsat.py
    .venv/bin/python scripts/extract_landsat.py --sensors landsat8 --years 2015 2016
    .venv/bin/python scripts/extract_landsat.py --all-bands --first-year 1999 --last-year 2020

With ``--all-bands``, the four other reflective bands are added, for the
100 m circle only, and the files go to ``data/processed/landsat_bands/``.

It needs the ``satellite`` dependencies and the Earth Engine setup described
in the README.
"""

import argparse
import sys
import time

import pandas as pd

from mn_desertification import satellite as sat
from mn_desertification.paths import PROCESSED_DIR
from mn_desertification.rules import CHECK_FOOTPRINT_M, EXTRACT_FIRST, EXTRACT_LAST, FOOTPRINT_M

# The summers each sensor was taking scenes. Landsat 5 ended in 2011 and
# Landsat 7 in early 2024. The weather record ends in 2024.
YEARS = {
    "landsat5": range(1984, 2012),
    "landsat7": range(1999, 2024),
    "landsat8": range(2013, 2025),
    "landsat9": range(2022, 2025),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sensors", nargs="+", default=list(YEARS), choices=list(YEARS))
    parser.add_argument("--years", nargs="+", type=int, help="only these years")
    parser.add_argument("--first-year", type=int, help="no year before this one")
    parser.add_argument("--last-year", type=int, help="no year after this one")
    parser.add_argument("--workers", type=int, default=4, help="requests waiting on Earth Engine at once")
    parser.add_argument("--all-bands", action="store_true", help="add blue, green and the two shortwave-infrared bands")
    args = parser.parse_args()

    out_dir = PROCESSED_DIR / ("landsat_bands" if args.all_bands else "landsat")
    radii = (FOOTPRINT_M,) if args.all_bands else (FOOTPRINT_M, CHECK_FOOTPRINT_M)
    out_dir.mkdir(parents=True, exist_ok=True)
    sat.connect()
    sites = pd.read_csv(PROCESSED_DIR / "sites.csv")

    jobs = [(sensor, year) for sensor in args.sensors for year in YEARS[sensor]
            if (not args.years or year in args.years)
            and (args.first_year is None or year >= args.first_year)
            and (args.last_year is None or year <= args.last_year)
            and not (out_dir / f"{sensor}_{year}.csv").exists()]
    print(f"{len(jobs)} sensor-years to extract into {out_dir}", flush=True)

    failed = []
    for number, (sensor, year) in enumerate(jobs, start=1):
        began = time.time()
        start, end = sat.season_dates(year, EXTRACT_FIRST, EXTRACT_LAST)
        try:
            table = sat.landsat_observations(sensor, sites, start, end, radii, args.workers, args.all_bands)
        except Exception as error:  # a failed request; the next run tries this sensor-year again
            failed.append((sensor, year))
            print(f"[{number}/{len(jobs)}] {sensor} {year}: FAILED, {str(error).splitlines()[0][:150]}", flush=True)
            continue
        table.insert(0, "sensor", sensor)
        # Times are written to the second, in one format for every row
        table.to_csv(out_dir / f"{sensor}_{year}.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
        print(f"[{number}/{len(jobs)}] {sensor} {year}: {len(table)} rows, "
              f"{table['overpass'].nunique()} overpasses, {table['gid'].nunique()} sites, {time.time() - began:.0f} s", flush=True)

    if failed:
        print(f"{len(failed)} sensor-years failed. Run the script again to retry them: {failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
