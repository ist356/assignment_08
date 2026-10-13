"""
dashboard.py — Salt City: Where Should We Open Next?

    streamlit run code/dashboard.py

Four tabs, each answering one of the owner's questions. The page only assembles:
every table comes from the saltcity package and every chart from charts.py.
"""
import streamlit as st
from streamlit_folium import st_folium

from pipeline import run
from saltcity import (
    REASONS,
    busy_table,
    close,
    demand_by_zip,
    make_choropleth,
    make_heatmap,
    make_shop_map,
    make_trend,
    make_violin,
    members_by_zip,
    monthly_sales,
    reason_table,
    site_scores,
)

st.set_page_config(page_title="Salt City: Where Should We Open Next?", layout="wide")
st.title("Salt City: Where Should We Open Next?")

data = run()
shops, zips, customers = data["shops"], data["zips"], data["customers"]
orders, visits = data["orders"], data["visits"]
our_shops = shops.loc[shops["kind"] == "ours", "shop"].tolist()

# The heading, the data, the tabs, and the When we're busy and Where we are tabs are
# provided. You write the other two tabs: Why they come (step 4) and Where to open
# next (step 6). The tests (pytest tests/test_pipeline.py -k dashboard) check them.
#
# Only the open tab runs (on_change="rerun"), so a picker on one tab never redraws
# the others' charts. That is why each tab's code sits under `if <tab>.open:`.
busy, why, where, next_shop = st.tabs(
    ["When we're busy", "Why they come", "Where we are", "Where to open next"],
    key="tab", on_change="rerun")

# 3. WHEN WE'RE BUSY  (provided)
if busy.open:
    with busy:
        choice = st.selectbox("Shop", ["All shops"] + our_shops, key="busy_shop")
        shop = None if choice == "All shops" else choice
        fig = make_heatmap(busy_table(orders, shop),
                           f"Orders by day and hour: {choice}")
        st.pyplot(fig)
        close(fig)
        left, right = st.columns(2)
        with left:
            st.plotly_chart(make_trend(monthly_sales(orders)))
        with right:
            fig = make_violin(orders)
            st.pyplot(fig)
            close(fig)

# 4. WHY THEY COME  — you write this tab.
#    a. choice <- st.selectbox("Shop", ["All shops"] + our_shops, key="why_shop"),
#       just like When we're busy. shown <- the visits at that shop (or all of them).
#    b. One st.metric per reason, in settings.REASONS order: how many of `shown`
#       got it (value_counts(), then .reindex(REASONS, fill_value=0) so a reason
#       with no visits still shows 0), side by side in st.columns.
#    c. make_heatmap(reason_table(visits, the shop or None), a title naming the
#       choice) — your classifier's eye test. st.pyplot(fig), then close(fig).
#    d. Two columns, the same charts as When we're busy but broken down by reason,
#       for the visits in `shown`: make_trend(monthly_sales(shown, "reason"),
#       "reason", "orders") with st.plotly_chart, and make_violin(shown, "reason")
#       with st.pyplot (and close).
if why.open:
    with why:
        # TODO: steps 4a-4d
        st.info("Why they come: your tab goes here.")

# 5. WHERE WE ARE  (provided)
if where.open:
    with where:
        st_folium(make_shop_map(shops, orders), height=500, use_container_width=True,
                  returned_objects=[], key="shops")

# 6. WHERE TO OPEN NEXT  — you write this tab.
#    a. Two columns, two choropleths with the shops on top (make_choropleth(...,
#       shops)): members_by_zip(customers) colored by "members" — "Where members
#       live"; demand <- demand_by_zip(visits), colored by "visits" — "Where
#       members are when they buy".
#    b. scores <- site_scores(demand, zips, shops) (provided); a third choropleth
#       colored by "score".
#    c. winner <- the first row of scores. st.success naming its ZIP, its visits and
#       how far the nearest Salt City shop is (ours_km).
#    d. st.dataframe of the top 10 scores (hide_index=True).
if next_shop.open:
    with next_shop:
        # TODO: steps 6a-6d
        st.info("Where to open next: your tab goes here.")
