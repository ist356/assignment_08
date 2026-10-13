"""
analysis.py — the tables behind the charts, and the site score.

Each function returns a small DataFrame a chart builder (charts.py) can draw. No
loops: pandas' pivot_table, groupby and merge do the work.
"""

import geopandas as gpd
import numpy as np
import pandas as pd

from .geo import haversine_km, zip_centers
from .settings import (
    DAY_NAMES,
    NEAR_HOME,
    OPEN_HOURS,
    REASONS,
    RIVAL_KM,
    RIVAL_PENALTY,
    SERVED_KM,
    WORKDAY_REASONS,
)


def busy_table(orders: pd.DataFrame, shop: str | None = None) -> pd.DataFrame:
    """Orders by day of the week (rows) and hour of the day (columns).

    Rows are settings.DAY_NAMES (Mon ... Sun) in order; columns are the hours in
    settings.OPEN_HOURS (6 ... 21). Each cell is the number of orders placed in
    that hour on that day over the whole year — 0 where there were none. With
    `shop`, only that shop's orders count.

    How to build it:

    - Filter to `shop` when one is given.
    - Day name and hour from `timestamp`: `.dt.dayofweek` (0 = Monday) mapped
      through DAY_NAMES, and `.dt.hour`.
    - `pivot_table(index="day", columns="hour", values="order_id",
      aggfunc="count", fill_value=0)`.
    - `.reindex(index=DAY_NAMES, columns=OPEN_HOURS, fill_value=0)` puts every
      day and hour in order, even ones with no orders.
    """
    # TODO: your code here
    pass


def reason_table(visits: pd.DataFrame, shop: str | None = None) -> pd.DataFrame:
    """Visits by reason (rows, in settings.REASONS order) and hour (columns,
    settings.OPEN_HOURS) — the "eye test" for your classifier. With `shop`, only
    that shop's visits count.

    Built like busy_table, with `reason` instead of the day and `hour` truncated
    to a whole number (`.astype(int)`).
    """
    # TODO: your code here
    pass


def monthly_sales(orders: pd.DataFrame, by: str = "shop") -> pd.DataFrame:
    """Sales per month, broken down by the column `by`: columns `month`
    ("2025-11" ...), `by`, `sales` (sum of `total`, rounded to cents) and `orders`
    (count), sorted by month then `by`.

        monthly_sales(orders)                  one row per month and shop
        monthly_sales(visits, by="reason")     one row per month and visit reason

    How to build it:

    - `month` <- `timestamp.dt.strftime("%Y-%m")`.
    - `groupby(["month", by])` and `.agg(sales=("total", "sum"),
      orders=("order_id", "count"))`, then `reset_index()`.
    """
    # TODO: your code here
    pass


def members_by_zip(customers: pd.DataFrame) -> pd.DataFrame:
    """How many members *live* in each ZIP: columns `zip`, `members`, most first.

    `customers` comes from add_zips (it has `home_zip`). Members whose home is in
    no ZIP are left out.
    """
    # TODO: your code here
    pass


def add_anchor_zip(visits: pd.DataFrame) -> pd.DataFrame:
    """`visits` with an `anchor_zip` column: the ZIP that visit is evidence of
    demand in.

    - a workday reason (settings.WORKDAY_REASONS): the member's `work_zip`;
    - NEAR_HOME: the member's `home_zip`;
    - OTHER: missing — it says nothing about a place.

    `np.select` with those two conditions and `default=None` builds it in one
    line. A new DataFrame; `visits` is not changed.
    """
    # TODO: your code here
    pass


def demand_by_zip(visits: pd.DataFrame) -> pd.DataFrame:
    """How many visits each ZIP *anchors* — where members are when they buy:
    columns `zip`, `visits`, most first. Visits with no anchor are left out.

    Calls add_anchor_zip, then counts `anchor_zip` like members_by_zip counts
    `home_zip`.
    """
    # TODO: your code here
    pass


def site_scores(demand: pd.DataFrame, zips: gpd.GeoDataFrame,
                shops: pd.DataFrame) -> pd.DataFrame:
    """Score every ZIP as the place for shop #4, best first.

    `demand` is demand_by_zip's table. Returns one row per ZIP in `zips`:

        zip  visits  ours_km  rival_km  served  score  rank

    - `visits`: from `demand` (0 for a ZIP that anchors none).
    - `ours_km` / `rival_km`: km from the ZIP's center (zip_centers) to the
      nearest of *our* shops / the nearest rival (`kind` in shops), rounded to 2.
    - `served`: True when `ours_km` <= settings.SERVED_KM — we already have a shop
      there, so it is not a candidate.
    - `score`: 0 when served; otherwise `visits`, times settings.RIVAL_PENALTY
      when `rival_km` <= settings.RIVAL_KM.
    - `rank`: 1 for the highest score (`score.rank(ascending=False,
      method="first")` as int), sorted by rank.

    How to build it:

    - centers <- zip_centers(zips); merge `demand` on `zip` (how="left") and fill
      missing visits with 0.
    - For the nearest shop: merge the centers with our shops using
      `how="cross"` (every center with every shop), compute haversine_km on the
      columns, then `groupby("zip")[...].min()`. Same for the rivals.
    """
    # TODO: your code here
    pass
