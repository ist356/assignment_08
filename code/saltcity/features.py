"""
features.py — turn each order into a *visit* with the facts a classifier needs.

An order says who, where and when. To guess *why*, you need more: how far the
shop is from the member's home and from their work, whether it was on the way
between the two, what time of day and which day of the week it was. Those
columns are *features* — the raw material for the rules you write in classify.py.

add_features builds the features every classifier needs (the columns below). Add
any others you find useful: more columns are fine.
"""

import pandas as pd

from .geo import haversine_km


def add_features(orders: pd.DataFrame, customers: pd.DataFrame,
                 shops: pd.DataFrame) -> pd.DataFrame:
    """One row per order with the member's points, the shop's point and features.

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

    How to build it:

    - Merge `orders` with `customers` on `customer_id` (how="left"), then with
      `shops[["shop", "lat", "lon"]]` renamed to `shop_lat` / `shop_lon` on `shop`.
    - `hour` <- `.dt.hour + .dt.minute / 60` of `timestamp`; `weekday` <-
      `.dt.dayofweek < 5` (Monday is 0).
    - `has_work` <- `work_lat` is not missing (`.notna()`).
    - The three distances with haversine_km on whole columns (see geo.py).
    """
    # TODO: your code here
    pass
