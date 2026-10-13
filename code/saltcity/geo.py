"""
geo.py — distances, and which ZIP code a point is in.

`haversine_km` is provided. You write `add_zips` and `zip_centers` with GeoPandas
(Lesson 6-4).
"""

import geopandas as gpd
import numpy as np
import pandas as pd

from .settings import LATLON_CRS, METERS_CRS


def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line ("as the crow flies") distance in kilometers.  *(Provided.)*

    Works on single numbers or on whole pandas columns at once:

        haversine_km(43.0480, -76.1545, 43.0405, -76.1185)   ->  3.02
        visits["d_home"] = haversine_km(visits["home_lat"], visits["home_lon"],
                                        visits["shop_lat"], visits["shop_lon"])

    A missing coordinate (NaN) gives a missing distance (NaN).
    """
    lat1, lon1, lat2, lon2 = (np.radians(np.asarray(x, dtype=float))
                              for x in (lat1, lon1, lat2, lon2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    km = 6371.0 * 2 * np.arcsin(np.sqrt(a))
    return km.item() if np.ndim(km) == 0 else km


def points_in_zips(frame: pd.DataFrame, lat: str, lon: str,
                   zips: gpd.GeoDataFrame) -> pd.Series:
    """The ZIP code each row's (`lat`, `lon`) point falls in, as a Series aligned
    with `frame` (missing where the point is missing or outside every ZIP).

        points_in_zips(customers, "home_lat", "home_lon", zips)
        -> 0    13041
           1    13027
           ...

    How to build it:

    - Keep the rows whose point is not missing: `frame.dropna(subset=[lat, lon])`.
    - Turn them into a GeoDataFrame of points: `gpd.GeoDataFrame(rows,
      geometry=gpd.points_from_xy(rows[lon], rows[lat]), crs=LATLON_CRS)` —
      x is longitude, y is latitude.
    - `gpd.sjoin(points, zips[["zip", "geometry"]], how="left",
      predicate="within")` — a *spatial* join: each point gets the `zip` of the
      polygon it is within.
    - Return its `zip` column, re-indexed to `frame.index` (`.reindex(frame.index)`)
      so the missing rows come back as NaN.
    """
    # TODO: your code here
    pass


def add_zips(customers: pd.DataFrame, zips: gpd.GeoDataFrame) -> pd.DataFrame:
    """`customers` with two new columns, `home_zip` and `work_zip` — the ZIP code
    each member's Home and Work point falls in (missing when there is no point).

    A new DataFrame; `customers` itself is not changed.

    How to build it:

    - Copy `customers`.
    - `home_zip` <- points_in_zips(the copy, "home_lat", "home_lon", zips);
      `work_zip` the same with the work columns.
    """
    # TODO: your code here
    pass


def zip_centers(zips: gpd.GeoDataFrame) -> pd.DataFrame:
    """The center of each ZIP code: a DataFrame with columns `zip`, `lat`, `lon`.

    A polygon's center is its *centroid*. Computing it in latitude/longitude gives
    a slightly wrong answer (degrees are not the same size everywhere), so:

    - `zips.to_crs(METERS_CRS).centroid` — the centers, measured in meters;
    - `.to_crs(LATLON_CRS)` — back to latitude/longitude;
    - build the DataFrame from `zips["zip"]`, the points' `.y` (lat) and `.x` (lon).
    """
    # TODO: your code here
    pass
