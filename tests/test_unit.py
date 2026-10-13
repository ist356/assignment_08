"""Unit tests — every function on small inputs you can check by hand.

The data is in helpers.py: three members (one commutes from Clay to downtown, one
lives by Westcott with no saved Work, one commutes from Clay to the Carrier Circle
corridor), six orders, and three square made-up "ZIP codes". Nothing here needs
the network or the full data set.
"""

import math

import folium
import matplotlib.pyplot as plt
import pandas as pd
import pytest
from helpers import (
    CUSTOMERS,
    SHOPS,
    assert_unmodified,
    count_kind,
    obvious_reasons,
    orders,
    snapshot,
    squares,
)

from saltcity import (
    REASONS,
    add_anchor_zip,
    add_features,
    add_zips,
    busy_table,
    classify_visits,
    demand_by_zip,
    haversine_km,
    make_choropleth,
    make_heatmap,
    make_shop_map,
    make_trend,
    make_violin,
    members_by_zip,
    monthly_sales,
    reason_table,
    site_scores,
    zip_centers,
)
from saltcity.settings import DAY_NAMES, OPEN_HOURS, REASON_COLORS


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def visits(with_zips: bool = False) -> pd.DataFrame:
    customers = add_zips(CUSTOMERS, squares()) if with_zips else CUSTOMERS
    return add_features(orders(), customers, SHOPS)


def classified() -> pd.DataFrame:
    return classify_visits(visits(with_zips=True))


# --- geo.py ---------------------------------------------------------------------------


def test_add_zips():
    before = snapshot(CUSTOMERS)
    out = add_zips(CUSTOMERS, squares())
    assert_unmodified(CUSTOMERS, before, "add_zips")
    assert {"home_zip", "work_zip"} <= set(out.columns), "add_zips should add home_zip and work_zip"
    assert len(out) == 3, "add_zips should keep one row per member"
    home = dict(zip(out["customer_id"], out["home_zip"]))
    work = dict(zip(out["customer_id"], out["work_zip"]))
    assert home[2] == "10001", f"member 2 lives inside ZIP 10001, got {home[2]!r}"
    assert pd.isna(home[1]), "member 1 lives in Clay, outside every test ZIP: home_zip should be missing"
    assert work[1] == "10001" and work[3] == "10003", f"work ZIPs should be 10001 and 10003, got {work}"
    assert pd.isna(work[2]), "member 2 has no saved Work: work_zip should be missing"


def test_zip_centers():
    out = zip_centers(squares())
    assert list(out.columns) == ["zip", "lat", "lon"], f"columns should be zip, lat, lon — got {list(out.columns)}"
    center = out.set_index("zip").loc["10001"]
    assert center["lat"] == pytest.approx(43.05, abs=0.002), "10001's center should be near latitude 43.05"
    assert center["lon"] == pytest.approx(-76.15, abs=0.002), "10001's center should be near longitude -76.15"


# --- features.py ----------------------------------------------------------------------


def test_add_features_columns_and_order():
    handed = orders()
    before = snapshot(handed)
    out = add_features(handed, CUSTOMERS, SHOPS)
    assert_unmodified(handed, before, "add_features")
    needed = {"home_lat", "home_lon", "work_lat", "work_lon", "shop_lat", "shop_lon",
              "hour", "weekday", "has_work", "d_home", "d_work", "detour"}
    missing = needed - set(out.columns)
    assert not missing, f"add_features is missing columns {sorted(missing)}"
    assert list(out["order_id"]) == list(handed["order_id"]), "add_features should keep the orders' rows and order"


def test_add_features_values():
    out = visits().set_index("order_id")
    assert out.loc[1, "hour"] == pytest.approx(7.5), "7:30 a.m. should be hour 7.5"
    assert out.loc[3, "hour"] == pytest.approx(17 + 10 / 60), "5:10 p.m. should be hour 17.1667"
    assert bool(out.loc[1, "weekday"]) and not bool(out.loc[4, "weekday"]), "Tuesday is a weekday; Saturday is not"
    assert bool(out.loc[1, "has_work"]) and not bool(out.loc[4, "has_work"]), "member 2 has no saved Work"
    want = haversine_km(43.039, -76.112, 43.0405, -76.1185)
    assert out.loc[4, "d_home"] == pytest.approx(want, abs=0.01), "d_home: km from home to the shop"
    assert out.loc[1, "d_work"] == pytest.approx(haversine_km(43.049, -76.152, 43.0480, -76.1545), abs=0.01)
    assert out.loc[1, "detour"] < 0.6, "Armory Square is right on member 1's way downtown: a small detour"
    assert out.loc[5, "detour"] > 5, "University Hill is far off member 3's commute: a big detour"
    assert pd.isna(out.loc[4, "d_work"]) and pd.isna(out.loc[4, "detour"]), "no Work: d_work and detour are missing"


# --- classify.py ----------------------------------------------------------------------


def test_classify_visits_contract():
    handed = visits(with_zips=True)
    before = snapshot(handed)
    out = classify_visits(handed)
    assert_unmodified(handed, before, "classify_visits")
    assert "reason" in out.columns, "classify_visits should add a reason column"
    assert list(out["order_id"]) == list(handed["order_id"]), "classify_visits should keep every row, in order"
    bad = set(out["reason"]) - set(REASONS)
    assert not bad, f"every reason must be one of settings.REASONS — found {sorted(bad)}"


def test_classify_visits_textbook_cases():
    """Six visits whose reason is not in doubt. Any sensible rules get these right."""
    out = dict(zip(classified()["order_id"], classified()["reason"]))
    wrong = {i: (out[i], want) for i, want in obvious_reasons().items() if out[i] != want}
    assert not wrong, "these obvious visits got the wrong reason (order: (yours, expected)): " + str(wrong)


# --- analysis.py ----------------------------------------------------------------------


def test_busy_table():
    out = busy_table(orders())
    assert list(out.index) == DAY_NAMES, "rows should be Mon ... Sun, in order"
    assert list(out.columns) == OPEN_HOURS, "columns should be the hours 6 ... 21"
    assert out.loc["Tue", 7] == 1 and out.loc["Sat", 10] == 1 and out.loc["Sun", 9] == 1
    assert int(out.to_numpy().sum()) == 6, "every order counts once"
    only = busy_table(orders(), "Westcott")
    assert int(only.to_numpy().sum()) == 2, "with a shop, only that shop's orders count"


def test_reason_table():
    out = reason_table(classified())
    assert list(out.index) == REASONS and list(out.columns) == OPEN_HOURS
    assert out.loc["on the way to work", 7] == 1 and out.loc["on the way home", 17] == 1
    assert int(out.to_numpy().sum()) == 6
    only = reason_table(classified(), "Westcott")
    assert int(only.to_numpy().sum()) == 2 and only.loc["near home", 10] == 1, (
        "with a shop, only that shop's visits count")


def test_monthly_sales():
    out = monthly_sales(orders())
    assert list(out.columns[:4]) == ["month", "shop", "sales", "orders"], f"columns: {list(out.columns)}"
    rows = {(r.month, r.shop): (r.sales, r.orders) for r in out.itertuples()}
    assert rows[("2026-03", "Armory Square")] == (pytest.approx(16.20), 3)
    assert rows[("2026-04", "Westcott")] == (pytest.approx(3.25), 1)
    assert len(out) == 4, "one row per month and shop that has orders"
    reasons = monthly_sales(classified(), by="reason")
    assert list(reasons.columns[:4]) == ["month", "reason", "sales", "orders"], (
        "with by='reason', the breakdown column is reason")
    rows = {(r.month, r.reason): r.orders for r in reasons.itertuples()}
    assert rows[("2026-03", "near home")] == 1 and rows[("2026-04", "near home")] == 1


def test_members_by_zip():
    out = members_by_zip(add_zips(CUSTOMERS, squares()))
    assert list(out.columns) == ["zip", "members"]
    assert out.to_dict("records") == [{"zip": "10001", "members": 1}], (
        "only member 2 lives inside a test ZIP; members with no home ZIP are left out")


def test_add_anchor_zip_and_demand():
    handed = classified()
    out = add_anchor_zip(handed).set_index("order_id")["anchor_zip"]
    assert out[1] == "10001" and out[2] == "10001", "workday visits anchor to the WORK ZIP"
    assert out[4] == "10001", "near-home visits anchor to the HOME ZIP"
    assert pd.isna(out[5]), "'other' visits anchor nowhere"
    demand = demand_by_zip(handed)
    assert list(demand.columns) == ["zip", "visits"]
    assert demand.to_dict("records") == [{"zip": "10001", "visits": 5}]


def test_site_scores():
    demand = pd.DataFrame({"zip": ["10001", "10002", "10003"], "visits": [100, 60, 40]})
    out = site_scores(demand, squares(), SHOPS)
    assert list(out.columns) == ["zip", "visits", "ours_km", "rival_km", "served", "score", "rank"]
    rows = out.set_index("zip")
    assert bool(rows.loc["10001", "served"]), "10001's center is next to Armory Square: served"
    assert rows.loc["10001", "score"] == 0, "a served ZIP scores 0"
    assert rows.loc["10002", "score"] == pytest.approx(30), "Lakeshore Lattes is in 10002: 60 visits x 0.5"
    assert rows.loc["10003", "score"] == pytest.approx(40), "10003 has no shop and no rival nearby: 40"
    assert list(out["zip"]) == ["10003", "10002", "10001"] and list(out["rank"]) == [1, 2, 3], (
        "best first, rank 1 to 3")


# --- charts.py ------------------------------------------------------------------------


def test_make_heatmap():
    table = busy_table(orders())
    fig = make_heatmap(table, "Test")
    assert isinstance(fig, plt.Figure), "make_heatmap should return the matplotlib Figure"
    meshes = [c for c in fig.axes[0].collections if c.get_array() is not None]
    assert meshes and meshes[0].get_array().size == 7 * 16, "one cell per day and hour (7 x 16)"
    assert fig.axes[0].get_title() == "Test", "use the title it is given"


def test_make_violin():
    frame = pd.concat([orders()] * 3, ignore_index=True)
    fig = make_violin(frame)
    assert isinstance(fig, plt.Figure), "make_violin should return the matplotlib Figure"
    labels = [t.get_text() for t in fig.axes[0].get_xticklabels()]
    assert sorted(labels) == sorted(frame["shop"].unique()), f"one violin per shop, got {labels}"
    by_reason = make_violin(pd.concat([classified()] * 3, ignore_index=True), "reason")
    labels = [t.get_text() for t in by_reason.axes[0].get_xticklabels()]
    assert labels == REASONS, f"by='reason': one violin per reason, in settings.REASONS order — got {labels}"


def test_make_trend():
    fig = make_trend(monthly_sales(orders()))
    assert len(fig.data) == 3, "one line per shop"
    assert all(trace.type == "scatter" for trace in fig.data), "make_trend should be a Plotly line chart"
    names = {trace.name for trace in fig.data}
    assert names == {"Armory Square", "Westcott", "University Hill"}
    by_reason = make_trend(monthly_sales(classified(), "reason"), "reason", "orders")
    assert {trace.name for trace in by_reason.data} == set(REASONS), "one line per reason"
    assert by_reason.data[0].line.color == REASON_COLORS[by_reason.data[0].name], (
        "each reason keeps its color from settings.REASON_COLORS")


def test_make_shop_map():
    fmap = make_shop_map(SHOPS, orders())
    assert isinstance(fmap, folium.Map)
    assert count_kind(fmap, folium.CircleMarker) == 3, "one CircleMarker per Salt City shop"
    assert count_kind(fmap, folium.Marker) == 3, "one Marker per rival"
    radii = sorted(c.options["radius"] for c in fmap._children.values() if type(c) is folium.CircleMarker)
    assert radii[-1] == pytest.approx(24) and radii[0] < radii[-1], (
        "radius = 6 + 18 x revenue / the largest revenue: the busiest shop gets 24")


def test_make_choropleth():
    table = pd.DataFrame({"zip": ["10001", "10003"], "members": [7, 2]})
    fig = make_choropleth(squares(), table, "members", "Test", SHOPS)
    trace = fig.data[0]
    assert trace.type == "choroplethmap", f"the first trace should be a choropleth map, got {trace.type}"
    values = dict(zip(trace.locations, trace.z))
    assert values == {"10001": 7, "10002": 0, "10003": 2}, f"every ZIP, missing ones as 0 — got {values}"
    assert len(fig.data) == 2 and len(fig.data[1].lat) == 6, "with shops, add them as a second trace"
    assert not math.isnan(fig.layout.map.zoom), "set a zoom"
