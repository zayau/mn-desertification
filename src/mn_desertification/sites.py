"""Placing the monitoring sites in soums and in seasonal pastures."""

import numpy as np
import pandas as pd
import shapely


def assign_soums(sites: pd.DataFrame, outlines: dict) -> pd.DataFrame:
    """The soum outline that contains each site.

    ``sites`` needs ``lon`` and ``lat``; ``outlines`` maps a soum's map
    ``_ID`` to its polygon (``data.read_soum_outlines``). Returns a copy of
    ``sites`` with two columns added: ``soum_id``, the map ``_ID`` of the
    site's soum (-1 if none), and ``n_hits``, how many outlines contain it.

    Some provincial centres are small soums inside a larger soum whose outline
    has no hole for them, so a site there lies inside both. Going from the
    largest soum to the smallest lets the small soum, which comes last, win.
    """
    areas = pd.Series({soum_id: polygon.area for soum_id, polygon in outlines.items()})
    placed = sites.copy()
    placed["soum_id"] = -1
    placed["n_hits"] = 0
    for soum_id in areas.sort_values(ascending=False).index:
        inside = shapely.contains_xy(outlines[soum_id], placed["lon"], placed["lat"])
        placed.loc[inside, "soum_id"] = soum_id
        placed.loc[inside, "n_hits"] += 1
    return placed


def outlines_around(sites: pd.DataFrame, outlines: np.ndarray, area_of_outline: np.ndarray) -> pd.Series:
    """How many outlines of each pasture area contain each site.

    ``outlines`` and ``area_of_outline`` come from
    ``data.read_pasture_outlines``. Returns a count indexed by site (``gid``)
    and area number, for the pairs where the count is above zero. A spatial
    index (``STRtree``) finds the few outlines near each site without testing
    all of them.
    """
    points = shapely.points(sites["lon"], sites["lat"])
    site_number, outline_number = shapely.STRtree(outlines).query(points, predicate="within")
    hits = pd.DataFrame({
        "gid": sites["gid"].to_numpy()[site_number],
        "area": area_of_outline[outline_number],
    })
    return hits.groupby(["gid", "area"]).size()


def pasture_type(gids: pd.Series, counts: pd.Series, area_names: pd.Series) -> pd.Series:
    """The seasonal pasture at each site, or "outside map".

    ``counts`` comes from ``outlines_around``. A pasture area is drawn as many
    outlines, and some of them are holes cut out of larger ones. A site inside
    one outline is in the area; a site inside an outline and also inside a hole
    in it lies within two outlines but is not in the area. So a site is in an
    area when an odd number of the area's outlines contain it.

    Returns a Series aligned with ``gids``. Raises an error if a site falls in
    more than one area.
    """
    inside = counts[counts % 2 == 1].reset_index()[["gid", "area"]]
    if inside["gid"].duplicated().any():
        raise ValueError("A site lies in more than one pasture area.")
    pasture_of_site = inside.set_index("gid")["area"].map(area_names)
    return gids.map(pasture_of_site).fillna("outside map").rename("pasture")


def agrees_with_direction(sites: pd.DataFrame, outlines: np.ndarray, area_of_outline: np.ndarray) -> bool:
    """Whether the odd-count rule of ``pasture_type`` agrees with outline direction.

    In the map, as in shapefiles, outer outlines run clockwise and holes
    counterclockwise. Counting +1 for each outer outline and -1 for each hole
    around a site gives a positive total exactly when the site is inside the
    area. Returns True if both rules place every site the same way.
    """
    is_hole = shapely.is_ccw(shapely.get_exterior_ring(outlines))
    points = shapely.points(sites["lon"], sites["lat"])
    site_number, outline_number = shapely.STRtree(outlines).query(points, predicate="within")
    around = pd.DataFrame({
        "gid": sites["gid"].to_numpy()[site_number],
        "area": area_of_outline[outline_number],
        "sign": np.where(is_hole[outline_number], -1, 1),
    })
    by_area = around.groupby(["gid", "area"])["sign"]
    odd_count = by_area.size() % 2 == 1
    more_outer_than_holes = by_area.sum() > 0
    return bool((odd_count == more_outer_than_holes).all())
