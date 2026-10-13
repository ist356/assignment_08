"""
explore.py — run the pipeline one step at a time.  *(Provided.)*

    python code/explore.py

Each step prints what it made. Run it with the "Python Debugger: Current File"
launch configuration and set a breakpoint inside one of your functions to watch it
work on the real data — far easier than debugging inside the dashboard.
"""

from saltcity import (
    add_features,
    add_zips,
    busy_table,
    classify_visits,
    demand_by_zip,
    load_customers,
    load_orders,
    load_shops,
    load_zips,
    members_by_zip,
    site_scores,
)


def show(title: str, frame) -> None:
    """Print a heading and the first rows of a table."""
    print(f"\n=== {title} ===")
    print(frame.head(8).to_string())


if __name__ == "__main__":
    shops, zips = load_shops(), load_zips()
    customers = add_zips(load_customers(), zips)
    show("customers with their ZIPs", customers)
    orders = load_orders()
    visits = add_features(orders, customers, shops)
    show("visits with features", visits)
    visits = classify_visits(visits)
    print("\n=== reasons ===")
    print(visits["reason"].value_counts().to_string())
    show("Armory Square, orders by day and hour", busy_table(orders, "Armory Square"))
    show("where members live", members_by_zip(customers))
    demand = demand_by_zip(visits)
    show("where members are when they buy", demand)
    show("site scores", site_scores(demand, zips, shops))
