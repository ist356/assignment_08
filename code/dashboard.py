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
    make_journey_map,
    make_shop_map,
    make_trend,
    make_violin,
    members_by_zip,
    monthly_sales,
    reason_table,
    site_scores,
)

# --- The page: the algorithm, step by step ------------------------------------------
#
# Write the code for each step below its comment. The tests
# (pytest tests/test_pipeline.py -k dashboard) check the title, the tabs, the
# pickers, the metrics, the maps and the decision.
#
# 1. HEADING AND DATA
#    st.set_page_config(page_title=..., layout="wide") — first.
#    st.title: Salt City: Where Should We Open Next?
#    data <- run()  (pipeline.py: every table, built once and cached)
#    shops, zips, customers, orders, visits <- the entries of data
#    our_shops <- the names of the shops whose kind is "ours"
#
# 2. FOUR TABS: st.tabs(["When we're busy", "Why they come", "Where we are",
#                        "Where to open next"])
#
# 3. WHEN WE'RE BUSY
#    a. choice <- st.selectbox("Shop", ["All shops"] + our_shops, key="busy_shop")
#    b. The heatmap: busy_table(orders, the shop — or None for "All shops"), drawn
#       by make_heatmap with a title naming the choice. Show a matplotlib Figure
#       with st.pyplot(fig), then close(fig) to free it.
#    c. Two columns: make_trend(monthly_sales(orders)) with st.plotly_chart, and
#       make_violin(orders) with st.pyplot (and close).
#
# 4. WHY THEY COME
#    a. choice <- st.selectbox("Shop", ["All shops"] + our_shops, key="why_shop"),
#       just like step 3. shown <- the visits at that shop (or all of them).
#    b. One st.metric per reason, in settings.REASONS order: how many of `shown`
#       got it (value_counts(), then .reindex(REASONS, fill_value=0) so a reason
#       with no visits still shows 0), side by side in st.columns.
#    c. make_heatmap(reason_table(visits, the shop or None), a title naming the
#       choice) — your classifier's eye test.
#    d. member <- st.selectbox("Follow one member", the 40 customer_ids with the
#       most visits in `shown`, key="member")
#       st_folium(make_journey_map(visits, member), height=450,
#                 use_container_width=True, returned_objects=[], key="journey")
#       (returned_objects=[] means the page does not rerun when someone pans the map.)
#
# 5. WHERE WE ARE
#    st_folium(make_shop_map(shops, orders), ...) the same way, key="shops".
#
# 6. WHERE TO OPEN NEXT
#    a. Two columns, two choropleths with the shops on top:
#       members_by_zip(customers) colored by "members" — "Where members live";
#       demand_by_zip(visits) colored by "visits" — "Where members are when they buy".
#    b. scores <- site_scores(demand, zips, shops); a third choropleth colored by
#       "score".
#    c. winner <- the first row of scores. st.success naming its ZIP, its visits and
#       how far the nearest Salt City shop is.
#    d. st.dataframe of the top 10 scores (hide_index=True).
