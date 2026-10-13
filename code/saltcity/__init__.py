"""saltcity — Salt City Coffee's loyalty data: where should shop #4 go?"""

from .analysis import (
    add_anchor_zip,
    busy_table,
    demand_by_zip,
    members_by_zip,
    monthly_sales,
    reason_table,
    site_scores,
)
from .charts import (
    close,
    make_choropleth,
    make_heatmap,
    make_journey_map,
    make_shop_map,
    make_trend,
    make_violin,
)
from .classify import classify_visits
from .data import load_customers, load_orders, load_shops, load_zips
from .features import add_features
from .geo import add_zips, haversine_km, points_in_zips, zip_centers
from .scorer import report, score, score_table
from .settings import REASONS

__all__ = [
    "REASONS",
    "add_anchor_zip",
    "add_features",
    "add_zips",
    "busy_table",
    "classify_visits",
    "close",
    "demand_by_zip",
    "haversine_km",
    "load_customers",
    "load_orders",
    "load_shops",
    "load_zips",
    "make_choropleth",
    "make_heatmap",
    "make_journey_map",
    "make_shop_map",
    "make_trend",
    "make_violin",
    "members_by_zip",
    "monthly_sales",
    "points_in_zips",
    "reason_table",
    "report",
    "score",
    "score_table",
    "site_scores",
    "zip_centers",
]
