"""
settings.py — names, paths and numbers the whole package shares.  *(Provided.)*

You do not change this file, but you do need to read it: the visit reasons, the
site-score rules and how to reach the scorer are all defined here, once.

Your API key
------------
The scorer lives on the CENT iSchool IoT Portal (https://portal.app.cent-su.org),
the same portal as Assignment 06, and needs your key in an `X-API-KEY` header.
Put it in a file named `.env` at the root of this repository, one line:

    CENT_API_KEY=your-key-here

`.env` is in `.gitignore`, so git will not offer to commit it. A Codespaces
secret named `CENT_API_KEY` works too.
"""

import os

from dotenv import load_dotenv

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
CACHE_DIR = os.path.join(REPO_ROOT, "cache")

SHOPS_FILE = os.path.join(DATA_DIR, "shops.csv")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.csv")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
ZIPS_FILE = os.path.join(DATA_DIR, "syracuse_zips.geojson")

# --- Visit reasons -----------------------------------------------------------------
# The five labels the survey (and the scorer) use. Spell them exactly like this.
ON_THE_WAY_TO_WORK = "on the way to work"
DURING_WORK = "during work"
ON_THE_WAY_HOME = "on the way home"
NEAR_HOME = "near home"
OTHER = "other"
REASONS = [ON_THE_WAY_TO_WORK, DURING_WORK, ON_THE_WAY_HOME, NEAR_HOME, OTHER]

# Visits that happen because of the job: they count toward the member's WORK ZIP.
# NEAR_HOME counts toward the HOME ZIP; OTHER counts toward neither.
WORKDAY_REASONS = [ON_THE_WAY_TO_WORK, DURING_WORK, ON_THE_WAY_HOME]

# --- The site score -----------------------------------------------------------------
SERVED_KM = 2.5        # a ZIP whose center is this close to one of our shops is served
RIVAL_KM = 2.5         # a rival this close to a ZIP's center ...
RIVAL_PENALTY = 0.5    # ... halves that ZIP's score

# Distances and centers need meters, not degrees: UTM zone 18N covers Syracuse.
METERS_CRS = "EPSG:32618"
LATLON_CRS = "EPSG:4326"

# --- Charts -------------------------------------------------------------------------
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
OPEN_HOURS = list(range(6, 22))            # 6 a.m. through the 9 p.m. hour
SYRACUSE = (43.06, -76.14)                 # map center
REASON_COLORS = {
    ON_THE_WAY_TO_WORK: "blue",
    DURING_WORK: "purple",
    ON_THE_WAY_HOME: "orange",
    NEAR_HOME: "green",
    OTHER: "gray",
}

# --- The scorer ---------------------------------------------------------------------
BASE_URL = os.environ.get("CENT_API_BASE", "https://portal.app.cent-su.org")
SCORE_TASK = "salt-city-coffee/visit-reasons"   # POST {BASE_URL}/api/score/{SCORE_TASK}


def get_api_key() -> str:
    """Your portal API key, from the CENT_API_KEY environment variable or `.env`."""
    load_dotenv(os.path.join(REPO_ROOT, ".env"))
    key = os.environ.get("CENT_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "No API key found. Create a file named .env at the root of the repository "
            "containing one line, CENT_API_KEY=your-key-here (your key is on the Home "
            "page of https://portal.app.cent-su.org)."
        )
    return key
