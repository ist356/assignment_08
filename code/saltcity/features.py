"""
features.py — turn each order into a *visit* with the facts a classifier needs.
*(Provided.)*

An order says who, where and when. To guess *why*, you need more: how far the
shop is from the member's home and from their work, whether it was on the way
between the two, what time of day and which day of the week it was. Those
columns are *features* — the raw material for the rules you write in classify.py.

add_features builds the features every classifier needs (the columns below).
Read it: these columns are what your rules in classify.py work with. You may add
your own features here too (a per-member feature, say) — more columns are fine.
"""

import pandas as pd

from .geo import haversine_km


def add_features(orders: pd.DataFrame, customers: pd.DataFrame,
                 shops: pd.DataFrame) -> pd.DataFrame:
    """One row per order with the member's points, the shop's point and features.
    *(Provided.)*

    `customers` may already carry `home_zip` / `work_zip` (from add_zips); they
    come along. Returns a new DataFrame, in the same order as `orders`, with at
    least these columns besides the order's own:

        home_lat, home_lon, work_lat, work_lon   from customers
        shop_lat, shop_lon                       from shops (lat, lon renamed)
        hour       time of day as a decimal: 7:45 a.m. -> 7.75
        weekday    True Monday-Friday, False on weekends
        has_work   True when the member has a saved Work point
        d_home     km from home to the shop
        d_work     km from work to the shop (missing when no Work)
        detour     km the shop adds to the trip between home and work:
                   d_home + d_work - (home to work)   (missing when no Work)

    How it works: two merges (orders + members, then + shops), then each feature
    is one line on whole columns — no loops.
    """
    visits = orders.merge(customers, on="customer_id", how="left")
    shop_points = shops[["shop", "lat", "lon"]].rename(columns={"lat": "shop_lat",
                                                               "lon": "shop_lon"})
    visits = visits.merge(shop_points, on="shop", how="left")

    visits["hour"] = visits["timestamp"].dt.hour + visits["timestamp"].dt.minute / 60
    visits["weekday"] = visits["timestamp"].dt.dayofweek < 5
    visits["has_work"] = visits["work_lat"].notna()

    visits["d_home"] = haversine_km(visits["home_lat"], visits["home_lon"],
                                    visits["shop_lat"], visits["shop_lon"])
    visits["d_work"] = haversine_km(visits["work_lat"], visits["work_lon"],
                                    visits["shop_lat"], visits["shop_lon"])
    commute = haversine_km(visits["home_lat"], visits["home_lon"],
                           visits["work_lat"], visits["work_lon"])
    visits["detour"] = visits["d_home"] + visits["d_work"] - commute
    return visits
