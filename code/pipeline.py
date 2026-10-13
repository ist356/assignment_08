"""
pipeline.py — load the data and run every step once.  *(Provided.)*

The dashboard and check_score.py both start here, so the steps happen in one
place, in one order:

    shops, customers (+ home_zip / work_zip), orders, zips
    visits  <- add_features(orders, customers, shops), then classify_visits

`run()` caches its answer for the life of the Streamlit server, so changing a tab
does not redo it. Edit your code and Streamlit reruns it.
"""

import streamlit as st

from saltcity import (
    add_features,
    add_zips,
    classify_visits,
    load_customers,
    load_orders,
    load_shops,
    load_zips,
)


def build() -> dict:
    """Every table the dashboard needs, in a dict."""
    shops = load_shops()
    zips = load_zips()
    customers = add_zips(load_customers(), zips)
    orders = load_orders()
    visits = classify_visits(add_features(orders, customers, shops))
    return {"shops": shops, "zips": zips, "customers": customers,
            "orders": orders, "visits": visits}


@st.cache_data(show_spinner="Loading a year of orders...")
def run() -> dict:
    """build(), cached."""
    return build()
