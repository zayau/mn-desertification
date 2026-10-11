"""Readers for the tables and maps of the Purevjav et al. 2025 release.

Each reader loads only the columns it needs and gives them clear names. Stata
stores the soum code (``asid``) and the year of the soum table as decimals;
they become integers so that tables join cleanly. Other columns keep the
types they are stored with, so that results match those computed earlier.

The folders default to those in ``paths`` and can be passed in instead, for
example to read another copy of the data.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import shapely

from . import paths
from .rules import SHEEP_UNITS


def read_biomass(tables_dir: Path | None = None) -> pd.DataFrame:
    """August biomass at NAMEM's monitoring sites, one row per site and year.

    Columns: ``lon``, ``lat``, ``gid`` (the site), ``year`` and ``bms``, the
    air-dried biomass clipped in August, in centners per hectare
    (1 c/ha = 100 kg/ha). 18,152 rows at 1,488 sites, 2007–2020.
    """
    tables_dir = tables_dir or paths.TABLES_DIR
    return pd.read_stata(tables_dir / "bms_plot.dta")


def read_soum_weather(tables_dir: Path | None = None) -> pd.DataFrame:
    """Weather on each soum's summer grazing range, one row per soum and year.

    Columns: ``asid`` (the soum), ``year``, ``zone`` (the soum's dominant
    ecological zone), ``rain_spring`` (March–May, mm), ``rain_summer``
    (June–August, mm), ``rain_growing`` (the two added) and ``temp_summer``
    (mean June–August temperature, °C). The release's rain is all
    precipitation, snow included (notebook 9).

    The release's year runs from 1 September to 31 August and is named after
    the year in which it ends, so the summer of year 2017 is June–August 2017,
    the summer of the August 2017 clipping.
    """
    tables_dir = tables_dir or paths.TABLES_DIR
    names = {
        "eco": "zone",
        "sgr_spr_prec": "rain_spring",
        "sgr_smr_prec": "rain_summer",
        "sgr_smr_tmp_ave": "temp_summer",
    }
    weather = pd.read_stata(tables_dir / "wrk_soum.dta", columns=["asid", "year", *names])
    weather = weather.rename(columns=names)
    weather["asid"] = weather["asid"].astype(int)
    weather["year"] = weather["year"].astype(int)
    weather["rain_growing"] = weather["rain_spring"] + weather["rain_summer"]
    return weather[["asid", "year", "zone", "rain_spring", "rain_summer", "rain_growing", "temp_summer"]]


def read_greenness(indices=("ndvi",), tables_dir: Path | None = None) -> pd.DataFrame:
    """MODIS vegetation indices at each site, one row per site and year, 2000–2024.

    ``indices`` picks any of ``ndvi``, ``evi``, ``savi``, ``msavi``, ``nirv``
    and ``ndwi``. The values come from MODIS reflectance at 500 m resolution,
    taken within 100 m of each plot (Purevjav et al. 2025, supplementary text
    pp. S2 and S4). The file name says they are for August.
    """
    tables_dir = tables_dir or paths.TABLES_DIR
    names = {f"{index}_sm_ave": index for index in indices}
    greenness = pd.read_stata(tables_dir / "vegi_plot_modis_aug.dta", columns=["gid", "year", *names])
    return greenness.rename(columns=names)


def read_herd_before_summer(tables_dir: Path | None = None) -> pd.DataFrame:
    """Livestock counted in the December before each summer, in sheep units.

    Returns a table of soums (rows, ``asid``) by summers (columns), in millions
    of sheep units. Soums with no animals recorded get NaN, so that ratios
    between years stay finite.

    In the release, the sheep-unit columns (``su_cen_*``) carry the census of
    December t−1 under year t, the summer that follows it, while the head-count
    columns (``cen_*``) carry the calendar year. ``check_herd_timing`` shows
    this.
    """
    tables_dir = tables_dir or paths.TABLES_DIR
    census = pd.read_stata(tables_dir / "wrk_soum.dta", columns=["asid", "year", "su_cen_total"])
    census["asid"] = census["asid"].astype(int)
    census["year"] = census["year"].astype(int)
    herd = census.pivot(index="asid", columns="year", values="su_cen_total")
    return herd.where(herd > 0)


def read_census_head_counts(tables_dir: Path | None = None) -> pd.DataFrame:
    """Livestock from the December census in head, soums (rows) by calendar years.

    In millions of head. The head-count columns of the release carry the
    calendar year of the census, so the value for 2010 is the December 2010
    count, after the 2009–2010 dzud.
    """
    tables_dir = tables_dir or paths.TABLES_DIR
    census = pd.read_stata(tables_dir / "wrk_soum.dta", columns=["asid", "year", "cen_total"])
    census["asid"] = census["asid"].astype(int)
    census["year"] = census["year"].astype(int)
    return census.pivot(index="asid", columns="year", values="cen_total")


def check_herd_timing(tables_dir: Path | None = None) -> dict:
    """Which December the sheep-unit total of the release holds.

    Rebuilds sheep units from the head count of each species (``SHEEP_UNITS``)
    and returns the largest difference from ``su_cen_total`` when both come
    from the same year, and when the head counts come from the year before.
    """
    tables_dir = tables_dir or paths.TABLES_DIR
    columns = ["asid", "year", "su_cen_total"] + [f"cen_{name}" for name in SHEEP_UNITS]
    census = pd.read_stata(tables_dir / "wrk_soum.dta", columns=columns)
    census["asid"] = census["asid"].astype(int)
    census["year"] = census["year"].astype(int)
    census = census.sort_values(["asid", "year"])
    rebuilt = sum(weight * census[f"cen_{name}"] for name, weight in SHEEP_UNITS.items())
    year_before = rebuilt.groupby(census["asid"]).shift(1)
    return {
        "same year": float((census["su_cen_total"] - rebuilt).abs().max()),
        "year before": float((census["su_cen_total"] - year_before).abs().max()),
    }


def read_soum_outlines(maps_dir: Path | None = None) -> dict[int, shapely.Polygon]:
    """Soum outlines in longitude and latitude, keyed by the map's ``_ID``.

    The map is in Stata's format: one row per point of an outline, with an
    empty row before each soum. Each of the 339 soums is one outline. The
    lowercase columns ``_x`` and ``_y`` are longitude and latitude; the
    uppercase ones are projected plotting coordinates.
    """
    maps_dir = maps_dir or paths.MAPS_DIR
    points = pd.read_stata(maps_dir / "mn_soum_xy.dta", columns=["_ID", "_x", "_y"])
    points = points.dropna(subset=["_x", "_y"])  # drop the empty row before each soum
    return {
        int(soum_id): shapely.Polygon(zip(group["_x"], group["_y"]))
        for soum_id, group in points.groupby("_ID", sort=False)
    }


def read_soum_names(maps_dir: Path | None = None) -> pd.DataFrame:
    """Soum codes and names in English and Mongolian, one row per soum outline.

    The Mongolian names are stored as UTF-8 bytes read as Latin-1, which shows
    as text like ``Ð¥Ð¾Ð²Ð´``. Turning them back into bytes and reading those as
    UTF-8 repairs them.
    """
    maps_dir = maps_dir or paths.MAPS_DIR
    columns = ["_ID", "asid", "aimag_eng", "soum_eng", "aimag_mng", "soum_mng"]
    names = pd.read_stata(maps_dir / "mn_soum_db.dta", columns=columns)
    for column in ["aimag_mng", "soum_mng"]:
        names[column] = names[column].str.encode("latin-1").str.decode("utf-8")
    names["_ID"] = names["_ID"].astype(int)
    names["asid"] = names["asid"].astype(int)
    return names


def read_pasture_areas(maps_dir: Path | None = None) -> pd.DataFrame:
    """The 16 areas of the land agency's seasonal pasture map.

    Columns: ``area`` (the area number used by the outlines), ``range`` (for
    example "Winter-Spring Grazing Range, WGR"), ``type`` (the Mongolian name,
    such as Өвөлжөө for winter camps) and ``name_eng`` (``winter-spring``,
    ``summer-fall`` or ``pasture-not-used``).
    """
    maps_dir = maps_dir or paths.MAPS_DIR
    areas = pd.read_stata(maps_dir / "mn_pas_db.dta", columns=["_ID", "pasture", "type", "name_eng"])
    areas["_ID"] = areas["_ID"].astype(int)
    return areas.rename(columns={"_ID": "area", "pasture": "range"})


def read_pasture_outlines(maps_dir: Path | None = None):
    """The land agency's seasonal pasture map, as outlines.

    The map (2021 State Land Report; Purevjav et al. 2025, supplement p. S3)
    has 16 areas: winter-spring ranges, used December to May, summer-fall
    ranges, used June to November, an inter-soum reserve area and unused
    pasture. Each area is drawn as many outlines, some of them holes, with an
    empty row before each outline: 42 million rows in a 5.3 GB file.

    Returns three things: an array of outlines as shapely polygons, an array
    with the area number of each outline, and a Series of area names
    (``winter-spring``, ``summer-fall``, ``pasture-not-used``) indexed by area
    number. Reading takes about 15 seconds and briefly about 4 GB of memory.
    """
    maps_dir = maps_dir or paths.MAPS_DIR

    # Read 2 million rows at a time and keep only the area number and the
    # coordinates. The with block closes the large file when done.
    with pd.read_stata(maps_dir / "mn_pas_xy.dta", chunksize=2_000_000, columns=["_ID", "_x", "_y"]) as reader:
        points = pd.concat(reader, ignore_index=True)

    # An empty row starts each outline, so counting the empty rows seen so far
    # numbers the outlines. Renumbering them 0, 1, 2, ... is what shapely expects.
    new_outline = points["_x"].isna().to_numpy()
    outline_number = np.cumsum(new_outline)[~new_outline]
    area_number = points["_ID"].to_numpy()[~new_outline]
    lon_lat = points[["_x", "_y"]].to_numpy()[~new_outline]
    del points
    _, outline_index = np.unique(outline_number, return_inverse=True)

    # Build all the outlines at once from the long list of points.
    outlines = shapely.polygons(shapely.linearrings(lon_lat, indices=outline_index))
    area_of_outline = pd.Series(area_number).groupby(outline_index).first().to_numpy()

    area_names = read_pasture_areas(maps_dir).set_index("area")["name_eng"].rename("pasture")
    return outlines, area_of_outline, area_names
