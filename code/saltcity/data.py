"""
data.py — load the four data files.  *(Provided.)*

    shops      shop, kind ("ours" or "rival"), lat, lon
    customers  customer_id, joined, home_lat, home_lon, work_lat, work_lon
               (the loyalty app's saved Home and Work, rounded to about a city
               block; work_lat/work_lon are blank for members with no saved Work)
    orders     order_id, customer_id, shop, timestamp, items, total
    zips       the Syracuse-area ZIP codes as polygons (a GeoDataFrame: zip, geometry)
"""

import geopandas as gpd
import pandas as pd

from .settings import CUSTOMERS_FILE, ORDERS_FILE, SHOPS_FILE, ZIPS_FILE


def load_shops() -> pd.DataFrame:
    """Our three shops and the three rivals."""
    return pd.read_csv(SHOPS_FILE)


def load_customers() -> pd.DataFrame:
    """Loyalty members with their Home and Work points."""
    return pd.read_csv(CUSTOMERS_FILE)


def load_orders() -> pd.DataFrame:
    """A year of orders; `timestamp` is parsed into a datetime."""
    return pd.read_csv(ORDERS_FILE, parse_dates=["timestamp"])


def load_zips() -> gpd.GeoDataFrame:
    """ZIP code polygons (latitude/longitude, EPSG:4326), with `zip` as a string."""
    zips = gpd.read_file(ZIPS_FILE)
    zips["zip"] = zips["zip"].astype(str)
    return zips
