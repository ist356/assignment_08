"""Code structure tests — read the source and check how it is built.

The other tests check what your functions *return*. These check *how*: that the
ZIP codes come from a spatial join, the tables from pandas instead of loops, each
chart from the library its lesson teaches, and that the dashboard assembles the
package instead of redoing it.

Everything here reads the **parsed** source (`ast`), so a technique mentioned in a
comment does not count. When a test fails, the message names the file and the
thing it was looking for.
"""

import ast

from helpers import repo_path

GEO = "code/saltcity/geo.py"
FEATURES = "code/saltcity/features.py"
CLASSIFY = "code/saltcity/classify.py"
ANALYSIS = "code/saltcity/analysis.py"
CHARTS = "code/saltcity/charts.py"
DASHBOARD = "code/dashboard.py"


def parse(script: str) -> ast.Module:
    with open(repo_path(script), encoding="utf-8") as fh:
        return ast.parse(fh.read(), filename=script)


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def called_names(tree: ast.AST) -> set:
    return {call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)}


def attributes(tree: ast.AST) -> set:
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def strings(tree: ast.AST) -> set:
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)}


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name}() not found")


def imported_modules(tree: ast.Module) -> set:
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def loops(tree: ast.AST) -> list:
    return [node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))]


# --- Part 1: places and features ------------------------------------------------------


def test_zips_come_from_a_spatial_join():
    tree = parse(GEO)
    found = called_names(function(tree, "points_in_zips"))
    assert {"sjoin", "points_from_xy"} <= found, (
        f"{GEO}: points_in_zips should build points with gpd.points_from_xy and gpd.sjoin them to the ZIPs")
    assert "points_in_zips" in called_names(function(tree, "add_zips")), (
        f"{GEO}: add_zips should call points_in_zips() for home and work")
    centers = function(tree, "zip_centers")
    assert "to_crs" in called_names(centers) and "centroid" in attributes(centers), (
        f"{GEO}: zip_centers should project with .to_crs(...) and take the .centroid")


def test_features_use_merge_and_haversine():
    found = called_names(function(parse(FEATURES), "add_features"))
    assert "merge" in found and "haversine_km" in found, (
        f"{FEATURES}: add_features should merge the tables and measure with haversine_km")
    assert not loops(function(parse(FEATURES), "add_features")), (
        f"{FEATURES}: add_features should work on whole columns, not loop over rows")


def test_classifier_uses_time_and_distance():
    tree = function(parse(CLASSIFY), "classify_visits")
    used = strings(tree) | attributes(tree)
    time_features = {"hour", "weekday"} & used
    place_features = {"d_home", "d_work", "detour"} & used
    assert time_features and place_features, (
        f"{CLASSIFY}: classify_visits should use when the visit happened (hour, weekday) "
        "AND where (d_home, d_work, detour)")
    assert not imported_modules(parse(CLASSIFY)) & {"requests"}, (
        f"{CLASSIFY}: the classifier works on the visits — no calls to the network")


# --- Part 2: tables -------------------------------------------------------------------


def test_tables_use_pandas():
    tree = parse(ANALYSIS)
    for name in ("busy_table", "reason_table"):
        assert "pivot_table" in called_names(function(tree, name)), f"{ANALYSIS}: {name} should use pivot_table"
    assert "groupby" in called_names(function(tree, "monthly_sales")), (
        f"{ANALYSIS}: monthly_sales should use groupby")
    assert "add_anchor_zip" in called_names(function(tree, "demand_by_zip")), (
        f"{ANALYSIS}: demand_by_zip should call add_anchor_zip()")
    scores = called_names(function(tree, "site_scores"))
    assert {"zip_centers", "haversine_km"} <= scores, (
        f"{ANALYSIS}: site_scores should use zip_centers() and haversine_km()")
    for name in ("busy_table", "reason_table", "monthly_sales", "members_by_zip",
                 "add_anchor_zip", "demand_by_zip", "site_scores"):
        assert not loops(function(tree, name)), f"{ANALYSIS}: {name} should use pandas, not a for/while loop"


# --- Part 3: charts and the dashboard ---------------------------------------------------


def test_each_chart_uses_its_library():
    tree = parse(CHARTS)
    expect = {
        "make_heatmap": {"heatmap"},
        "make_violin": {"violinplot"},
        "make_trend": {"line"},
        "make_shop_map": {"Map", "CircleMarker", "Marker"},
        "make_journey_map": {"Map", "Marker", "PolyLine", "CircleMarker"},
        "make_choropleth": {"choropleth_map"},
    }
    for name, needed in expect.items():
        missing = needed - called_names(function(tree, name))
        assert not missing, f"{CHARTS}: {name} should call {sorted(missing)}"
    assert {"seaborn", "plotly", "folium"} <= imported_modules(tree), (
        f"{CHARTS} should import seaborn, plotly and folium")


def test_dashboard_assembles_the_package():
    tree = parse(DASHBOARD)
    called = called_names(tree)
    assert "saltcity" in imported_modules(tree) and "pipeline" in imported_modules(tree), (
        f"{DASHBOARD} should import from the saltcity package and pipeline.run()")
    needed = {"run", "tabs", "selectbox", "pyplot", "plotly_chart", "st_folium", "metric",
              "success", "dataframe", "busy_table", "reason_table", "monthly_sales",
              "members_by_zip", "demand_by_zip", "site_scores", "make_heatmap", "make_violin",
              "make_trend", "make_shop_map", "make_journey_map", "make_choropleth"}
    missing = needed - called
    assert not missing, f"{DASHBOARD} should call {sorted(missing)}"
    assert not called & {"groupby", "pivot_table", "sjoin", "heatmap", "violinplot", "merge",
                         "choropleth_map"}, (
        f"{DASHBOARD}: the page assembles — tables belong in analysis.py, charts in charts.py")
    assert "print" not in called, f"{DASHBOARD}: use widgets, not the console"
