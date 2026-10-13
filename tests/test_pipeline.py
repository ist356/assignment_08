"""Pipeline & app tests — the whole year of data, your classifier against the
survey, the decision, and the dashboard.

- The data steps run on data/ (about 36,000 orders and 3,370 members).
- Your classifier is scored by the CENT portal, exactly like
  `python code/check_score.py`; it needs your key in .env. To pass, your reasons
  must agree with the survey on at least 85% of visits overall and at least 60%
  of the visits of every single reason.
- The dashboard is driven with Streamlit's AppTest, the way opening it would.
"""

import pytest
from helpers import load_app, no_exception

from pipeline import build
from saltcity import (
    REASONS,
    busy_table,
    demand_by_zip,
    members_by_zip,
    monthly_sales,
    score,
    site_scores,
)

OVERALL_BAR = 0.85
LABEL_BAR = 0.60
DASHBOARD = "code/dashboard.py"


@pytest.fixture(scope="module")
def data():
    return build()


def test_add_zips_on_all_members(data):
    customers = data["customers"]
    assert len(customers) == 3370, f"expected all 3,370 members, got {len(customers)}"
    assert customers["home_zip"].notna().all(), "every member's home is inside one of the 31 ZIPs"
    has_work = customers["work_lat"].notna()
    assert customers.loc[has_work, "work_zip"].notna().all(), "every saved Work is inside a ZIP"


def test_members_by_zip_on_all_members(data):
    top = members_by_zip(data["customers"]).iloc[0]
    assert (top["zip"], top["members"]) == ("13041", 745), (
        f"the most members live in Clay (13041, 745 members) — got {tuple(top)}")


def test_add_features_on_all_orders(data):
    visits = data["visits"]
    assert len(visits) == len(data["orders"]) == 36067, "one visit per order"
    assert visits["d_home"].notna().all(), "every visit has a distance from home"
    assert (visits["d_work"].isna() == ~visits["has_work"]).all(), "d_work is missing exactly when there is no Work"


def test_classifier_agrees_with_the_survey(data):
    result = score(data["visits"])
    weak = {label: numbers["agreement"] for label, numbers in result["labels"].items()
            if numbers["agreement"] < LABEL_BAR}
    hint = "; ".join(
        f"{label} {numbers['agreement']:.2f} (often called {numbers['most_confused_with']})"
        for label, numbers in result["labels"].items() if label in weak)
    assert result["agreement"] >= OVERALL_BAR and not weak, (
        f"agreement {result['agreement']:.2f} (need {OVERALL_BAR}); every reason needs "
        f"{LABEL_BAR}. " + (f"Below: {hint}" if hint else "Run code/check_score.py for the table."))


def test_reasons_cover_every_label(data):
    counts = data["visits"]["reason"].value_counts()
    missing = [reason for reason in REASONS if counts.get(reason, 0) == 0]
    assert not missing, f"no visit gets these reasons: {missing}"


def test_busy_table_on_all_orders(data):
    orders = data["orders"]
    table = busy_table(orders, "Armory Square")
    assert int(table.to_numpy().sum()) == int((orders["shop"] == "Armory Square").sum())
    assert table.loc["Tue", 7] > 5 * table.loc["Sat", 7], "Armory Square's weekday 7 a.m. rush"


def test_monthly_sales_on_all_orders(data):
    table = monthly_sales(data["orders"])
    assert len(table) == 36, "12 months x 3 shops"
    assert table["sales"].sum() == pytest.approx(data["orders"]["total"].sum(), abs=1)


def test_the_decision(data):
    scores = site_scores(demand_by_zip(data["visits"]), data["zips"], data["shops"])
    assert len(scores) == 31, "one row per ZIP"
    assert scores.iloc[0]["zip"] == "13057", (
        f"with your reasons, the best site is {scores.iloc[0]['zip']} — the data points to 13057, "
        "the Carrier Circle corridor. Check your reasons and the anchors.")
    served = set(scores.loc[scores["served"], "zip"])
    assert {"13202", "13210"} <= served, "ZIPs with a Salt City shop are served"


def test_dashboard_loads():
    app = load_app(DASHBOARD)
    no_exception(app, DASHBOARD)
    assert app.title and "Salt City" in app.title[0].value, "title the page 'Salt City: ...'"
    labels = [tab.label for tab in app.tabs]
    assert len(labels) == 4, f"four tabs, got {labels}"


def test_dashboard_busy_tab():
    app = load_app(DASHBOARD, "When we're busy")
    no_exception(app, DASHBOARD)
    assert app.get("plotly_chart"), "the monthly trend (Plotly) on When we're busy"


def test_dashboard_shows_the_decision():
    app = load_app(DASHBOARD, "Where to open next")
    no_exception(app, DASHBOARD)
    assert any("13057" in box.value for box in app.success), "a st.success naming the winning ZIP"
    assert len(app.get("plotly_chart")) >= 3, "three choropleth maps (Plotly) on Where to open next"
    assert app.dataframe, "the site-score table"


def test_dashboard_tabs_are_lazy():
    app = load_app(DASHBOARD, "Where to open next")
    assert len(app.tabs) == 4 and app.success, "open on Where to open next, its content shows"
    assert not app.metric and not any(box.key == "busy_shop" for box in app.selectbox), (
        "only the open tab should run: st.tabs(..., key='tab', on_change='rerun') and "
        "`if tab.open:` around each tab")


def test_dashboard_shop_picker():
    app = load_app(DASHBOARD, "When we're busy")
    picker = next((box for box in app.selectbox if box.key == "busy_shop"), None)
    assert picker is not None, "a st.selectbox with key='busy_shop' to pick the shop"
    picker.select("Westcott").run()
    no_exception(app, DASHBOARD)


def test_dashboard_why_shop_picker():
    app = load_app(DASHBOARD, "Why they come")
    assert len(app.metric) == 5, "one metric per reason"
    picker = next((box for box in app.selectbox if box.key == "why_shop"), None)
    assert picker is not None, "a st.selectbox with key='why_shop' on the Why they come tab"
    picker.select("University Hill").run()
    no_exception(app, DASHBOARD)
    total = sum(int(str(m.value).replace(",", "")) for m in app.metric)
    assert 0 < total < 36067, "with one shop picked, the metrics count only that shop's visits"


def test_dashboard_member_picker():
    app = load_app(DASHBOARD, "Why they come")
    picker = next((box for box in app.selectbox if box.key == "member"), None)
    assert picker is not None, "a st.selectbox with key='member' to follow one member"
    picker.select(picker.options[1]).run()
    no_exception(app, DASHBOARD)
