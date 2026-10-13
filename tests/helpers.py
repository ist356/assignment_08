"""Shared helpers for the tests: small hand-made data, looking inside charts, and
driving the Streamlit page."""

import os

import folium
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from streamlit.testing.v1 import AppTest

# tests/ lives directly under the repository root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repo_path(*parts: str) -> str:
    """Build an absolute path from the repository root, whatever the working directory."""
    return os.path.join(REPO_ROOT, *parts)


def snapshot(frame: pd.DataFrame) -> pd.DataFrame:
    """A deep copy to compare against after a function has run."""
    return frame.copy(deep=True)


def assert_unmodified(handed: pd.DataFrame, before: pd.DataFrame, step: str) -> None:
    """The frame the function was handed still looks exactly like it did before the call."""
    assert list(handed.columns) == list(before.columns) and handed.astype(str).equals(before.astype(str)), (
        f"{step} modified the DataFrame it was given — work on a copy, or build a new frame."
    )


# --- Small, hand-checkable data -----------------------------------------------------
# Real places, so the distances make sense:
#   member 1 lives in Clay, works downtown (Armory Square is on the way)
#   member 2 lives by Westcott and has no saved Work
#   member 3 lives in Clay and works in the Carrier Circle corridor

SHOPS = pd.DataFrame([
    ("Armory Square", "ours", 43.0480, -76.1545),
    ("Westcott", "ours", 43.0405, -76.1185),
    ("University Hill", "ours", 43.0428, -76.1335),
    ("Canal Street Coffee", "rival", 43.0512, -76.1500),
    ("Hilltop Grind", "rival", 43.0392, -76.1290),
    ("Lakeshore Lattes", "rival", 43.1062, -76.2105),
], columns=["shop", "kind", "lat", "lon"])

CUSTOMERS = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "joined": ["2024-01-05", "2023-06-01", "2025-02-11"],
    "home_lat": [43.190, 43.039, 43.185],
    "home_lon": [-76.200, -76.112, -76.190],
    "work_lat": [43.049, None, 43.079],
    "work_lon": [-76.152, None, -76.070],
})

# (order_id, customer_id, shop, timestamp, items, total, the obvious reason)
ORDERS_AND_REASONS = [
    (1, 1, "Armory Square", "2026-03-03 07:30", 1, 4.25, "on the way to work"),     # Tuesday
    (2, 1, "Armory Square", "2026-03-03 12:30", 2, 8.20, "during work"),
    (3, 1, "Armory Square", "2026-03-03 17:10", 1, 3.75, "on the way home"),
    (4, 2, "Westcott", "2026-03-07 10:00", 4, 22.40, "near home"),                  # Saturday
    (5, 3, "University Hill", "2026-03-07 14:00", 1, 4.75, "other"),
    (6, 2, "Westcott", "2026-04-12 09:15", 1, 3.25, "near home"),                   # Sunday
]


def orders() -> pd.DataFrame:
    """The six hand-made orders (timestamps parsed), without their reasons."""
    frame = pd.DataFrame([row[:6] for row in ORDERS_AND_REASONS],
                         columns=["order_id", "customer_id", "shop", "timestamp", "items", "total"])
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    return frame


def obvious_reasons() -> dict:
    return {row[0]: row[6] for row in ORDERS_AND_REASONS}


def squares() -> gpd.GeoDataFrame:
    """Three made-up square "ZIP codes": 10001 around Armory Square, 10002 around
    Lakeshore Lattes (a rival), 10003 out in the corridor (nobody there)."""
    return gpd.GeoDataFrame({
        "zip": ["10001", "10002", "10003"],
        "geometry": [box(-76.20, 43.03, -76.10, 43.07),      # downtown + the Hill
                     box(-76.24, 43.09, -76.18, 43.12),      # Liverpool
                     box(-76.10, 43.06, -76.04, 43.10)],     # Carrier Circle
    }, crs="EPSG:4326")


# --- Looking inside charts ----------------------------------------------------------


def folium_children(fmap: folium.Map) -> list:
    """Every element added to a Folium map (markers, circles, lines ...)."""
    return list(fmap._children.values())


def count_kind(fmap: folium.Map, kind: type) -> int:
    return sum(type(child) is kind for child in folium_children(fmap))


# --- Streamlit ----------------------------------------------------------------------


def load_app(script: str, tab: str | None = None) -> AppTest:
    """Load a Streamlit script from the repository and run it once, as opening it
    would — with `tab` open, when the page has lazy st.tabs(key="tab")."""
    app = AppTest.from_file(repo_path(script), default_timeout=120)
    if tab is not None:
        app.session_state["tab"] = tab
    app.run()
    return app


def no_exception(app: AppTest, script: str) -> None:
    assert not app.exception, f"{script} raised: {app.exception[0].value}"
