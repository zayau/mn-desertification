"""Satellite greenness at the monitoring sites, extracted with Google Earth Engine.

Earth Engine keeps the satellite archives on Google's servers and computes
there. Most functions below only describe a piece of work: which images, which
weeks, which sites. Two of them, ``values_at_sites`` and
``values_through_time``, send the work and wait for the answer, which is a
small table. No image is downloaded.

Using this module needs the optional ``satellite`` dependencies, a Google
Cloud project registered for Earth Engine, and a sign-in on this computer
(``earthengine authenticate``, then ``earthengine set_project``).
"""

import datetime as dt
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor

import ee
import numpy as np
import pandas as pd

from .rules import FOOTPRINT_M, SEASON_FIRST, SEASON_LAST

# The MODIS product behind the release's site table: reflectance as seen from
# straight above (NBAR), in 500 m pixels, one image a day since February 2000.
MODIS_NBAR = "MODIS/061/MCD43A4"

# The Earth's mean radius, for distances of a few hundred metres.
EARTH_RADIUS_M = 6_371_000

# Greenness indices from red and near-infrared reflectance (0 to 1), written
# in the syntax of Earth Engine's expressions.
INDEX_FORMULAS = {
    # Normalised difference vegetation index
    "ndvi": "(nir - red) / (nir + red)",
    # Modified soil-adjusted vegetation index, in the form with no soil parameter
    "msavi": "(2 * nir + 1 - ((2 * nir + 1) ** 2 - 8 * (nir - red)) ** 0.5) / 2",
}


def connect(project: str | None = None) -> None:
    """Start a session with Earth Engine.

    With no ``project``, the one stored by ``earthengine set_project`` is used.
    """
    ee.Initialize(project=project)


def season_dates(year: int, first: tuple = SEASON_FIRST, last: tuple = SEASON_LAST) -> tuple[str, str]:
    """A season of one year as the two dates Earth Engine filters by.

    ``first`` and ``last`` are (month, day). Returns the first day and the day
    after the last one, because Earth Engine leaves the end date out.
    """
    start = dt.date(year, *first)
    end = dt.date(year, *last) + dt.timedelta(days=1)
    return start.isoformat(), end.isoformat()


def site_footprints(sites: pd.DataFrame, radius_m: float = FOOTPRINT_M) -> ee.FeatureCollection:
    """A circle of ``radius_m`` metres around each site, labelled with its ``gid``.

    ``sites`` needs ``gid``, ``lon`` and ``lat``.
    """
    circles = [
        ee.Feature(ee.Geometry.Point([float(lon), float(lat)]).buffer(radius_m), {"gid": int(gid)})
        for gid, lon, lat in zip(sites["gid"], sites["lon"], sites["lat"])
    ]
    return ee.FeatureCollection(circles)


def add_indices(image: ee.Image) -> ee.Image:
    """Add one band per index in ``INDEX_FORMULAS`` to an image with ``red`` and ``nir`` bands."""
    bands = {"red": image.select("red"), "nir": image.select("nir")}
    indices = [image.expression(formula, bands).rename(name) for name, formula in INDEX_FORMULAS.items()]
    return image.addBands(ee.Image.cat(*indices))


def modis_nbar(start: str, end: str, full_inversions_only: bool = False) -> ee.ImageCollection:
    """The daily MODIS images from ``start`` up to, not including, ``end``, with the index bands.

    Each daily value is fitted to the cloud-free observations of 16 days. The
    fit is a full inversion when there are enough observations and a
    lower-quality magnitude inversion otherwise. A pixel with too few
    observations for either has no value. ``full_inversions_only`` drops the
    values from magnitude inversions.
    """
    def prepare(image):
        # Reflectance is stored as whole numbers; 0.0001 brings it back to 0-1
        bands = image.select(["Nadir_Reflectance_Band1", "Nadir_Reflectance_Band2"], ["red", "nir"]).multiply(0.0001)
        if full_inversions_only:
            # The quality band of each reflectance band is 0 for a full inversion
            red_full = image.select("BRDF_Albedo_Band_Mandatory_Quality_Band1").eq(0)
            nir_full = image.select("BRDF_Albedo_Band_Mandatory_Quality_Band2").eq(0)
            bands = bands.updateMask(red_full.And(nir_full))
        # Arithmetic drops an image's date, so it is copied back
        return add_indices(bands).copyProperties(image, ["system:time_start"])

    return ee.ImageCollection(MODIS_NBAR).filterDate(start, end).map(prepare)


def modis_grid() -> ee.Projection:
    """The pixel grid of the MODIS product, to work on it without resampling."""
    return ee.ImageCollection(MODIS_NBAR).first().select(0).projection()


def season_composite(images: ee.ImageCollection, how: str = "median") -> ee.Image:
    """One image that summarises a season, pixel by pixel.

    Each index band holds the pixel's ``"median"``, ``"mean"`` or ``"max"``
    over the images in which it had a value. The band ``n_clear`` counts those
    images.
    """
    names = list(INDEX_FORMULAS)
    indices = images.select(names)
    summary = {"median": indices.median, "mean": indices.mean, "max": indices.max}[how]()
    n_clear = images.select(names[0]).count().rename("n_clear")
    return summary.addBands(n_clear)


def values_at_sites(image: ee.Image, footprints: ee.FeatureCollection, grid: ee.Projection,
                    tile_scale: int = 4) -> pd.DataFrame:
    """The mean of each band of ``image`` within each footprint, as a table.

    This sends the work to Earth Engine and waits for the answer. ``grid`` is
    the pixel grid to work on. A pixel counts by the share of it that lies
    inside the footprint, which Earth Engine measures in steps of about 1/256
    of a pixel. Returns one row per site (``gid``) and one column per band; a
    site with no value in a band has NaN there.

    Earth Engine computes an image in square blocks of pixels, and only the
    blocks that touch a footprint. ``tile_scale`` shrinks the side of the
    blocks by that factor, which saves computing when the footprints are small
    and far apart. It does not change the values.
    """
    reduced = image.reduceRegions(collection=footprints, reducer=ee.Reducer.mean(), crs=grid, tileScale=tile_scale)
    # Only the numbers come back, not the outlines of the footprints
    features = reduced.select([".*"], None, False).getInfo()["features"]
    table = pd.DataFrame([feature["properties"] for feature in features])
    return table.sort_values("gid", ignore_index=True)


def yearly_site_values(images_between: Callable[[str, str], ee.ImageCollection], footprints: ee.FeatureCollection,
                       grid: ee.Projection, years: Iterable[int], first: tuple = SEASON_FIRST,
                       last: tuple = SEASON_LAST, how: str = "median", workers: int = 5) -> pd.DataFrame:
    """Each site's seasonal greenness in each year, one request to Earth Engine per year.

    ``images_between`` gives the images between two dates, for example
    ``modis_nbar``. The season runs from ``first`` to ``last``, both
    (month, day), and is summarised as in ``season_composite``. Up to
    ``workers`` requests wait on Earth Engine at the same time. Returns one row
    per site and year with ``gid``, ``year``, a column per index and
    ``n_clear``.
    """
    columns = ["gid", "year", *INDEX_FORMULAS, "n_clear"]

    def one_year(year):
        start, end = season_dates(year, first, last)
        composite = season_composite(images_between(start, end), how)
        table = values_at_sites(composite, footprints, grid).assign(year=year)
        # A band with no value at any site comes back without its column
        return table.reindex(columns=columns)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        tables = list(pool.map(one_year, years))
    return pd.concat(tables, ignore_index=True)


def pixels_near(image: ee.Image, lon: float, lat: float, grid: ee.Projection, distance_m: float) -> pd.DataFrame:
    """Every pixel of ``image`` whose centre lies within ``distance_m`` of a point.

    This sends the work to Earth Engine and waits for the answer. Returns one
    row per pixel, nearest first, with a column per band and where the pixel's
    centre lies: its ``longitude`` and ``latitude``, how far east and north of
    the point it is (``east_m``, ``north_m``) and its ``distance_m``, all to
    within a few metres.
    """
    point = ee.Geometry.Point([lon, lat])
    located = image.addBands(ee.Image.pixelLonLat())
    features = located.sample(region=point.buffer(distance_m), projection=grid, dropNulls=False).getInfo()["features"]
    table = pd.DataFrame([feature["properties"] for feature in features])
    # A degree of latitude is the same length everywhere; a degree of longitude
    # shrinks with the cosine of the latitude
    table["east_m"] = np.radians(table["longitude"] - lon) * np.cos(np.radians(lat)) * EARTH_RADIUS_M
    table["north_m"] = np.radians(table["latitude"] - lat) * EARTH_RADIUS_M
    table["distance_m"] = np.hypot(table["east_m"], table["north_m"])
    return table.sort_values("distance_m", ignore_index=True)


def values_through_time(images: ee.ImageCollection, lon: float, lat: float, grid: ee.Projection) -> pd.DataFrame:
    """Every image's index values at the pixel that holds one point, by date.

    This sends the work to Earth Engine and waits for the answer. Returns one
    row per image with ``date`` and a column per index, NaN where the pixel
    had no value.
    """
    names = list(INDEX_FORMULAS)
    rows = images.select(names).getRegion(ee.Geometry.Point([lon, lat]), crs=grid).getInfo()
    table = pd.DataFrame(rows[1:], columns=rows[0])
    table["date"] = pd.to_datetime(table["time"], unit="ms")
    table[names] = table[names].astype(float)
    return table[["date", *names]].sort_values("date", ignore_index=True)
