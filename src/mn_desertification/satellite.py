"""Satellite greenness at the monitoring sites, extracted with Google Earth Engine.

Earth Engine keeps the satellite archives on Google's servers and computes
there. Most functions below only describe a piece of work: which images, which
weeks, which sites. A few send the work and wait for the answer, which is a
small table, and their descriptions say so. No image is downloaded.

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
import shapely

from .rules import CHECK_FOOTPRINT_M, FOOTPRINT_M, SEASON_FIRST, SEASON_LAST

# The MODIS product behind the release's site table: reflectance as seen from
# straight above (NBAR), in 500 m pixels, one image a day since February 2000.
MODIS_NBAR = "MODIS/061/MCD43A4"

# Landsat surface reflectance (Collection 2, Level 2, Tier 1) in 30 m pixels:
# each sensor's collection, its red band and its near-infrared band.
LANDSAT = {
    "landsat5": ("LANDSAT/LT05/C02/T1_L2", "SR_B3", "SR_B4"),
    "landsat7": ("LANDSAT/LE07/C02/T1_L2", "SR_B3", "SR_B4"),
    "landsat8": ("LANDSAT/LC08/C02/T1_L2", "SR_B4", "SR_B5"),
    "landsat9": ("LANDSAT/LC09/C02/T1_L2", "SR_B4", "SR_B5"),
}

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


def connect(project: str | None = None, patience_s: float = 600) -> None:
    """Start a session with Earth Engine.

    With no ``project``, the one stored by ``earthengine set_project`` is used.
    A request that has no answer after ``patience_s`` seconds fails, so that
    nothing waits forever.
    """
    ee.Initialize(project=project)
    ee.data.setDeadline(patience_s * 1000)


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


def site_circles(sites: pd.DataFrame, radii: Iterable[float] = (FOOTPRINT_M, CHECK_FOOTPRINT_M)) -> ee.FeatureCollection:
    """Circles of several radii around each site, labelled with ``gid`` and ``radius_m``.

    One request then serves the main footprint and the check.
    """
    circles = [
        ee.Feature(ee.Geometry.Point([float(lon), float(lat)]).buffer(radius), {"gid": int(gid), "radius_m": radius})
        for radius in radii
        for gid, lon, lat in zip(sites["gid"], sites["lon"], sites["lat"])
    ]
    return ee.FeatureCollection(circles)


def sites_box(sites: pd.DataFrame, margin: float = 0.1) -> ee.Geometry:
    """The box of longitudes and latitudes that holds every site, ``margin`` degrees wider on each side."""
    return ee.Geometry.Rectangle([sites["lon"].min() - margin, sites["lat"].min() - margin,
                                  sites["lon"].max() + margin, sites["lat"].max() + margin])


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
        # 1 where the pixel has a value in both bands, and no value elsewhere
        clear = bands.mask().reduce(ee.Reducer.min()).selfMask().rename("clear")
        # Arithmetic drops an image's date, so it is copied back
        prepared = add_indices(bands).addBands(clear).copyProperties(image, ["system:time_start"])
        return prepared.set("scene", image.get("system:index"))

    return ee.ImageCollection(MODIS_NBAR).filterDate(start, end).map(prepare)


def _clear_landsat(image: ee.Image, red_band: str, nir_band: str) -> ee.Image:
    """A Landsat scene as ``red``, ``nir``, the index bands and ``clear``, with values at clear pixels only."""
    # Stored as whole numbers; the scale and offset bring reflectance back to 0-1
    bands = image.select([red_band, nir_band], ["red", "nir"]).multiply(0.0000275).add(-0.2)
    # Bits 0 to 5 of the quality band: fill, dilated cloud, cirrus, cloud, cloud shadow, snow
    unflagged = image.select("QA_PIXEL").bitwiseAnd(0b111111).eq(0)
    # In the saturation band, bit n - 1 is set where band n is saturated
    saturated_bits = sum(1 << (int(band[-1]) - 1) for band in (red_band, nir_band))
    unsaturated = image.select("QA_RADSAT").bitwiseAnd(saturated_bits).eq(0)
    in_range = bands.gt(0).And(bands.lte(1)).reduce(ee.Reducer.min())
    clear = unflagged.And(unsaturated).And(in_range).selfMask().rename("clear")
    return add_indices(bands.updateMask(clear)).addBands(clear)


def landsat(sensor: str, start: str, end: str, region: ee.Geometry) -> ee.ImageCollection:
    """The scenes of one Landsat sensor over ``region``, from ``start`` up to, not including, ``end``.

    ``sensor`` is a key of ``LANDSAT``. Each scene comes back with ``red`` and
    ``nir`` (surface reflectance, 0 to 1), the index bands, and ``clear``,
    which is 1. All bands have values at clear pixels only. A pixel is clear
    when the quality band flags none of fill, cloud, dilated cloud, cirrus,
    cloud shadow and snow, when neither band is saturated, and when both
    reflectances lie between 0 and 1. Each scene is labelled with its name in
    the archive (``scene``).
    """
    collection, red_band, nir_band = LANDSAT[sensor]

    def prepare(image):
        # Arithmetic drops an image's date, so it is copied back
        prepared = _clear_landsat(image, red_band, nir_band).copyProperties(image, ["system:time_start"])
        return prepared.set("scene", image.get("system:index"))

    return ee.ImageCollection(collection).filterBounds(region).filterDate(start, end).map(prepare)


def landsat_scenes(sensor: str, start: str, end: str, region: ee.Geometry) -> pd.DataFrame:
    """A list of the scenes one Landsat sensor took over ``region``, with the ground each covers.

    This sends the work to Earth Engine and waits for the answer. Returns one
    row per scene: its name in the archive (``scene``), when it was taken
    (``time``, in UTC), the ground it covers (``outline``, a shapely polygon),
    and its ``overpass``. An overpass is one pass of the satellite, cut into
    scenes that overlap at their edges. It is labelled by its path, its date
    and the map zone of its pixel grid, which the scenes of one overpass share.
    """
    scenes = ee.ImageCollection(LANDSAT[sensor][0]).filterBounds(region).filterDate(start, end)
    listed = ee.FeatureCollection(scenes.map(lambda image: ee.Feature(image.geometry(), {
        "scene": image.get("system:index"), "time": image.get("system:time_start"), "path": image.get("WRS_PATH"),
        "date": image.get("DATE_ACQUIRED"), "zone": image.get("UTM_ZONE")}))).getInfo()["features"]
    if not listed:
        return pd.DataFrame(columns=["scene", "time", "overpass", "outline"])
    table = pd.DataFrame([feature["properties"] for feature in listed])
    table["outline"] = [shapely.geometry.shape(feature["geometry"]) for feature in listed]
    table["overpass"] = table["path"].map("{:03d}".format) + "_" + table["date"] + "_" + table["zone"].astype(str)
    table["time"] = pd.to_datetime(table["time"], unit="ms")
    return table[["scene", "time", "overpass", "outline"]].sort_values("time", ignore_index=True)


def sites_under_overpasses(scenes: pd.DataFrame, sites: pd.DataFrame) -> list[tuple]:
    """Which sites each overpass covers, worked out from the outlines of its scenes.

    ``scenes`` comes from ``landsat_scenes``. A site is covered when its plot
    lies inside one of the overpass's scenes. Returns one entry per overpass
    that covers a site: its label, the names of its scenes, the time of its
    first scene and the rows of ``sites`` it covers.
    """
    points = shapely.points(sites["lon"], sites["lat"])
    plan = []
    for overpass, group in scenes.groupby("overpass"):
        covered = sites[shapely.contains(shapely.union_all(group["outline"].to_list()), points)]
        if len(covered):
            plan.append((overpass, group["scene"].to_list(), group["time"].min(), covered))
    return plan


def landsat_observations(sensor: str, sites: pd.DataFrame, start: str, end: str,
                         radii: Iterable[float] = (FOOTPRINT_M, CHECK_FOOTPRINT_M), workers: int = 4) -> pd.DataFrame:
    """What every overpass of one Landsat sensor shows at every site it covers.

    This sends the work to Earth Engine and waits for the answer. The scenes
    from ``start`` up to, not including, ``end`` are listed first. Which sites
    each overpass covers is worked out here, from the outlines, so that Earth
    Engine is asked only for those. The scenes of an overpass are joined and
    read on their own pixel grid, and a site in the overlap of two scenes is
    counted once.

    Returns one row per site, radius and overpass: ``gid``, ``radius_m``,
    ``overpass``, ``time``, the mean ``red``, ``nir``, ``ndvi`` and ``msavi``
    of the clear pixels within the circle, and ``clear_pixels``, the number of
    clear pixels in the circle, with parts of pixels counted as parts. A
    circle with no clear pixel in an overpass has no row. Up to ``workers``
    requests wait on Earth Engine at the same time.
    """
    radii = list(radii)
    collection, red_band, nir_band = LANDSAT[sensor]
    wanted = {"gid": "gid", "radius_m": "radius_m", "overpass": "overpass", "time": "time", "red_mean": "red",
              "nir_mean": "nir", "ndvi_mean": "ndvi", "msavi_mean": "msavi", "clear_sum": "clear_pixels"}
    scenes = landsat_scenes(sensor, start, end, sites_box(sites))

    plan = sites_under_overpasses(scenes, sites)

    # Several overpasses share a request, as long as the answer stays under 4,000 rows
    batches, rows_so_far = [[]], 0
    for one in plan:
        rows = len(one[3]) * len(radii)
        if batches[-1] and (rows_so_far + rows > 4000 or len(batches[-1]) == 6):
            batches.append([])
            rows_so_far = 0
        batches[-1].append(one)
        rows_so_far += rows

    reducer = ee.Reducer.mean().combine(ee.Reducer.sum(), sharedInputs=True)

    def rows_of(overpass, scene_names, when, covered):
        images = [ee.Image(f"{collection}/{name}") for name in scene_names]
        joined = ee.ImageCollection([_clear_landsat(image, red_band, nir_band) for image in images]).mosaic()
        # A joined image forgets its pixel grid, so it is given the grid of its scenes
        joined = joined.setDefaultProjection(images[0].select(red_band).projection())
        rows = joined.reduceRegions(collection=site_circles(covered, radii), reducer=reducer, tileScale=4)
        # The time travels as milliseconds since 1970, like the times Earth Engine gives
        labels = {"overpass": overpass, "time": when.value // 1_000_000}
        return rows.filter(ee.Filter.gt("clear_sum", 0)).map(lambda row: row.set(labels))

    def ask(batch):
        rows = ee.FeatureCollection([rows_of(*one) for one in batch]).flatten()
        # Only the numbers come back, not the outlines of the circles
        features = rows.select([".*"], None, False).getInfo()["features"]
        return pd.DataFrame([feature["properties"] for feature in features]).reindex(columns=list(wanted))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        tables = list(pool.map(ask, [batch for batch in batches if batch]))
    table = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame(columns=list(wanted))
    table = table.rename(columns=wanted).astype({"gid": int})
    table["time"] = pd.to_datetime(table["time"], unit="ms")
    return table.sort_values(["gid", "radius_m", "time"], ignore_index=True)


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


def observations_at_sites(images: ee.ImageCollection, circles: ee.FeatureCollection) -> pd.DataFrame:
    """One row per circle and image: what the image shows within the circle.

    This sends the work to Earth Engine and waits for the answer. Earth Engine
    matches every circle against every image, which is slow for many of both,
    so this is for a few sites or a few images. ``landsat_observations`` does
    the same for all sites. Each image is read on its own pixel grid, and a
    pixel counts by the share of it that lies inside the circle.

    Returns ``gid``, ``radius_m``, ``scene`` (the image's label), ``time``
    (when it was taken, in UTC), the mean ``red``, ``nir``, ``ndvi`` and
    ``msavi`` of the clear pixels, and ``clear_pixels``, the number of clear
    pixels in the circle, with parts of pixels counted as parts. A circle with
    no clear pixel in an image has no row.
    """
    reducer = ee.Reducer.mean().combine(ee.Reducer.sum(), sharedInputs=True)

    def at_sites(image):
        here = circles.filterBounds(image.geometry())
        rows = image.reduceRegions(collection=here, reducer=reducer, tileScale=4)
        labels = {"scene": image.get("scene"), "time": image.get("system:time_start")}
        return rows.filter(ee.Filter.gt("clear_sum", 0)).map(lambda row: row.set(labels))

    rows = ee.FeatureCollection(images.map(at_sites)).flatten()
    wanted = {"gid": "gid", "radius_m": "radius_m", "scene": "scene", "time": "time", "red_mean": "red",
              "nir_mean": "nir", "ndvi_mean": "ndvi", "msavi_mean": "msavi", "clear_sum": "clear_pixels"}
    # A list of rows travels back, which has no limit on the number of rows
    values = rows.reduceColumns(ee.Reducer.toList(len(wanted)), list(wanted)).get("list").getInfo()
    table = pd.DataFrame(values, columns=list(wanted.values()))
    table["time"] = pd.to_datetime(table["time"], unit="ms")
    return table.astype({"gid": int}).sort_values(["gid", "radius_m", "time"], ignore_index=True)


def daily_values_at_sites(images: ee.ImageCollection, footprints: ee.FeatureCollection, grid: ee.Projection,
                          bands: Iterable[str] = ("red", "nir")) -> pd.DataFrame:
    """Some bands of every image at every footprint, with all the images in one request.

    This sends the work to Earth Engine and waits for the answer. It suits
    images that share a pixel grid and cover every site, as the daily MODIS
    images do, a month at a time. Returns one row per site and image:
    ``gid``, ``date`` and a column per band, the mean within the footprint.
    """
    bands = list(bands)
    # Stacked, each image's bands are named by its date, as in 2012_07_01_red
    wide = values_at_sites(images.select(bands).toBands(), footprints, grid)
    long = wide.melt(id_vars="gid", var_name="name", value_name="value")
    long["date"] = pd.to_datetime(long["name"].str.slice(0, 10), format="%Y_%m_%d")
    long["band"] = long["name"].str.slice(11)
    return long.pivot(index=["gid", "date"], columns="band", values="value")[bands].reset_index().rename_axis(columns=None)


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
