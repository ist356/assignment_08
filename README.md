# IST356 Assignment 08 — Where Should We Open Next?

Salt City Coffee has three shops — **Armory Square** downtown, **Westcott**, and
**University Hill** — and the owner is ready to open a fourth. Her first idea is the
obvious one: put it where the most loyalty members *live*. The map says that's
**Clay**, a big suburb north of the city with hundreds of members and no shop.

Before she signs a lease, she wants you to look at the data. The loyalty app knows
three things about every member: their saved **Home**, their saved **Work**, and every
**order** they placed — which shop, and when. You will turn that into a dashboard
that answers four questions: *When are we busy? Why do people come? Where are we and
the rivals? Where should shop #4 go?*

The twist is in the second question. People buy coffee where they *are* when they want
it — on the way to work, near work at lunch, near home on a Saturday. You will
engineer a classifier that works out **why** each visit happened from nothing but the
points and the clock, and check it against a survey you never get to see. Then you
will map where members live next to where they are when they buy — and find out
whether Clay is the right answer.

This is Unit 6 in one assignment: seaborn heatmaps and violins (6-1), Folium maps
(6-2), interactive Plotly charts (6-3), and GeoPandas with choropleths (6-4).

> **Plan for 6–12 hours, depending on your skill set, and start early.** Most of the
> functions are short and the charts are a few lines each. The part that takes time
> is the classifier: there is no single right answer, so you will try rules, score
> them, look at what they get wrong, and try again. That loop *is* the assignment.
> Commit after each part and submit early — GraderThan's feedback tells you which part
> to fix before you build on it.

## Meta

### Learning Objectives

By the end of this assignment you will be able to:

1. **Make a heatmap and a violin plot** with seaborn, and say what each one shows that a table doesn't
2. **Make an interactive chart** with Plotly, and show it in Streamlit
3. **Put data on a map** with Folium: markers, circles sized by a value, popups
4. **Work with geographic data** in GeoPandas: points from latitude/longitude, a **spatial join** (which polygon is each point in?), projections and centroids
5. **Draw a choropleth** that colors each ZIP code by a value
6. **Engineer features** (distance, detour, time of day) and **write a rule-based classifier**, then improve it against a validation set you can't see
7. **Turn a chart into a decision**: build a score, rank the options, and explain why the obvious answer was wrong

### Assignment Layout

- `code/` — **where you write code.** Only files in this folder are reviewed for grading.
  - `saltcity/` — the package
    - `__init__.py`, `settings.py`, `data.py`, `scorer.py` — **provided.** The public API; names, paths and numbers; loading the data; talking to the scorer
    - `geo.py` — **Part 1, you write this.** Which ZIP is each point in? (`haversine_km` is provided)
    - `features.py` — **Part 1, you write this.** Each order becomes a visit with features
    - `classify.py` — **Part 2, you design this.** Why did each visit happen?
    - `analysis.py` — **Part 3, you write this.** The tables behind the charts, and the site score
    - `charts.py` — **Part 3, you write this.** Every chart, returned by a function
  - `dashboard.py` — **Part 4, you write this** (a step-by-step algorithm is in the file)
  - `pipeline.py` — **provided.** Loads the data and runs every step once (cached for the dashboard)
  - `check_score.py` — **provided.** Sends your reasons to the scorer and prints how they did
  - `explore.py` — **provided.** Runs everything one step at a time so you can debug it
  - `reflection.txt` — **where you write your reflection** (graded)
- `data/` — `shops.csv`, `customers.csv`, `orders.csv` and `syracuse_zips.geojson` (see [About the data](#about-the-data--read-this-before-you-start))
- `cache/` — the scorer's answers you have already asked for. **Not committed**
- `tests/` — the automated tests
- `grader/` — the autograder used by GraderThan (you don't touch this)
- `.devcontainer/`, `.streamlit/`, `.vscode/` — container, Streamlit and editor configuration
- `README.md`, `reflection.md`, `rubric.json`, `requirements.txt`, `ruff.toml` — these instructions, reflection guidance, grading, dependencies, style rules

You write **seventeen functions** across five files — most are under ten lines and
come with a **How to build it** — one **classifier** you design yourself, and the
**dashboard**.

### Prerequisites

Same environment as Assignments 01–07. `pip install -r requirements.txt` (the container
does it for you) adds **GeoPandas, Plotly, Folium and streamlit-folium**.

You need your **CENT portal API key** from Assignment 06 for the scorer
([Reference #1](#1-how-do-i-set-up-my-api-key)).

---

## Prep — Open the assignment

Same as before: **first fork, then** open your fork in Codespaces (**Option A**) or a
local dev container (**Option B**).

1. **Fork this repository.** At the top-right of this repo's GitHub page, click **Fork**.
   You submit and are graded on *your fork*.

### Option A — GitHub Codespaces (in the browser) ⭐ easiest

1. On **your fork's** page, click **Code → Codespaces → Create codespace on main**.
2. VS Code opens in the browser, inside the course container, with Git signed in.

> Stop your Codespace when you're done (`github.com/codespaces` → **⋯ → Stop codespace**) —
> the free hours are monthly.

### Option B — Your own computer (local dev container)

1. Clone **your fork** (`Ctrl+Shift+P` → **Git: Clone**, or
   `git clone https://github.com/YOUR-GITHUB-USERNAME/assignment_08.git`).
2. **File → Open Folder** → `assignment_08` → **Reopen in Container**.

### Check you're ready

1. Create `.env` with your API key ([Reference #1](#1-how-do-i-set-up-my-api-key)).
2. Open the **Testing** panel and run the tests ([Reference #11](#11-how-do-i-run-automated-tests)).
   You should see **0 passing and 37 failing** — every test is about a function or page
   you haven't written yet.

---

## About the data — read this before you start

Everything is made up — the shops, the members, the orders — but it is laid out on the
real map of Syracuse, so the places will look familiar.

### The four files

| file | one row per | columns |
| --- | --- | --- |
| `shops.csv` | shop: our 3 and the 3 rivals from Assignment 07 | `shop`, `kind` ("ours" or "rival"), `lat`, `lon` |
| `customers.csv` | loyalty member (3,370) | `customer_id`, `joined`, `home_lat`, `home_lon`, `work_lat`, `work_lon` |
| `orders.csv` | order, November 2025 – October 2026 (36,067) | `order_id`, `customer_id`, `shop`, `timestamp`, `items`, `total` |
| `syracuse_zips.geojson` | ZIP code (31 around Syracuse) | `zip`, and the ZIP's outline as a polygon |

- **Home and Work** are what members saved in the app to order ahead. They are rounded to
  three decimal places — about a city block — so no one's exact address is stored.
  Students, retirees and people who work from home have **no Work**: those two columns
  are blank.
- The ZIP outlines are the U.S. Census Bureau's 2020 ZIP Code Tabulation Areas, cut down
  to Syracuse and simplified.

### Why did they come? Five reasons

The owner wants every visit sorted into one of five reasons (spelled exactly like this —
they are in `settings.REASONS`):

| reason | it means |
| --- | --- |
| `on the way to work` | stopped on the trip from home to work |
| `during work` | a break from work, near work |
| `on the way home` | stopped on the trip from work to home |
| `near home` | near where they live — weekends, a morning off, an evening out |
| `other` | none of these — an event, shopping, visiting a friend |

**Nobody told us the reasons.** The orders don't say why. You have to work it out from
*when* the visit happened and *where* the shop is compared to the member's home and work.

### The survey — and the scorer

The marketing team asked about 1,000 members, right in the app, "What brought you in
today?" Those answers are your **validation set** — but you never see them. They live
on the CENT portal, behind a **scorer**. You send a reason for *every* order; it compares
the ones it has answers for and tells you how well your rules agree:

```
$ python code/check_score.py
Sending 36,067 visits to the scorer...
salt-city-coffee/visit-reasons: 909 of 1000 survey visits agree (91%)

                   actual predicted correct mislabeled agreement  most_confused_with
label
on the way to work    411       393     371         40       0.9     on the way home
during work           167       167     152         15      0.91  on the way to work
on the way home       107       137     103          4      0.96  on the way to work
near home             275       258     249         26      0.91     on the way home
other                  40        45      34          6      0.85           near home
```

For each reason: **actual** is how many survey visits really were that reason,
**predicted** how many times you said it, **correct** how many you got right, and
**agreement** = correct ÷ actual. Read them together: `predicted` much bigger than
`actual` means that rule is catching visits it shouldn't — `most_confused_with` says
which ones.

You get a limited number of checks a day. Sending the *same* reasons again is free (the
answer is kept in `cache/`), so change something before you check again.

> **Is this machine learning?** Not quite. You're doing **rule-based classification**
> (also called heuristic labeling): the five reasons are decided up front, and you write
> the rules that assign them. It isn't *supervised* learning — you have no labeled
> examples to train on — and it isn't *unsupervised* learning either — you aren't letting
> an algorithm invent the groups. The scorer works like a validation set: it tells you
> how well your rules agree with the survey without showing you the answers. This is how
> many real projects start: write sensible rules, check them against a small survey,
> and only later train a model — sometimes on the labels your rules produced (that's
> called **weak supervision**).
>
> **Optional challenge:** cluster your features (for example k-means on hour, distance
> from home and distance from work), then name each cluster after one of the five
> reasons. The scorer grades that just as fairly.

### From reasons to a place

Once every visit has a reason, it is evidence of demand *somewhere*:

- a workday reason (on the way to work, during work, on the way home) → the member's
  **work ZIP**;
- `near home` → the member's **home ZIP**;
- `other` → nowhere in particular.

That ZIP is the visit's **anchor**. Count visits by anchor and you have *where members are
when they buy*. The **site score** turns that into a ranking: a ZIP whose center is within
2.5 km of one of our shops is already **served** (score 0); otherwise its score is the
visits it anchors, **halved** when a rival is within 2.5 km. The numbers are in
`settings.py`.

---

## Walkthrough — Do the assignment step by step

### How much help you get

| file | what you get |
| --- | --- |
| `geo.py`, `features.py`, `analysis.py`, `charts.py` | the contract, and a **How to build it** for most functions |
| `classify.py` | the five reasons and the contract. **The rules are yours.** |
| `dashboard.py` | the imports, then the page's algorithm as numbered comments |
| `pipeline.py`, `check_score.py`, `explore.py`, `scorer.py` | provided whole — read them, run them |

### Build order at a glance

| order | write this | turns green |
| --- | --- | --- |
| 1 | `points_in_zips`, `add_zips`, `zip_centers` | `test_unit.py -k "zips or centers"` |
| 2 | `add_features` | `test_unit.py -k features` |
| 3 | `classify_visits` — then score it, improve it, score again | `test_unit.py -k classify`, `test_pipeline.py -k classifier` |
| 4 | `busy_table`, `reason_table`, `monthly_sales`, `members_by_zip`, `add_anchor_zip`, `demand_by_zip`, `site_scores` | `test_unit.py -k "table or sales or members or anchor or site"` |
| 5 | `make_heatmap`, `make_violin`, `make_trend`, `make_shop_map`, `make_choropleth` | `test_unit.py -k make` |
| 6 | `dashboard.py` | `test_pipeline.py -k dashboard` |
| 7 | *(structure checks go green along the way)* | `test_code.py` |
| 8 | `reflection.txt` | — |

### Step 1 — Look before you code

Open the four files in `data/`. Pick a member in `customers.csv` and find their orders.
Paste a Home and a Work point into a map site. Which shop did they use, and when? You
are about to write code that does what you just did by eye, 36,067 times.

### Step 2 — Part 1: places (`geo.py`)

`points_in_zips` is a **spatial join**: points on one side, polygons on the other, and
each point gets the `zip` of the polygon it falls in
([Reference #2](#2-how-do-i-do-a-spatial-join-with-geopandas)). `add_zips` uses it twice,
for Home and for Work. `zip_centers` finds each ZIP's center — the one place you need a
**projection**.

### Step 3 — Part 1: features (`features.py`)

Merge the orders with the members and the shops, then compute the time of day, the day of
the week, and three distances: shop to home, shop to work, and the **detour** — how much
the shop adds to the trip between home and work
([Reference #3](#3-how-do-i-measure-distance-and-detour)). A shop right on the way adds
almost nothing; a shop across town adds a lot.

### Step 4 — Part 2: the classifier (`classify.py`)

This is the heart of the assignment. Start with the simplest rules you believe — the time
of day alone, say — and **score them** (`python code/check_score.py`). Then:

1. Look at the table. Which reason has the lowest agreement? What is it confused with?
2. Ask *what would tell those two apart?* Usually it's a place, not a time: a morning visit
   to a shop far off the commute isn't "on the way to work".
3. Change **one** thing, score again, and keep it only if it helped.

To pass, your reasons must agree with the survey on **at least 85%** of visits overall and
**at least 60%** of the visits of *every* reason — so you can't ignore the small ones.
Thoughtful rules get past 90%.

**The eye test.** Numbers aren't the only check. Once the dashboard draws the
*Why they come* tab — the reason-by-hour heatmap, the monthly lines and the violins — look at them:

- [ ] "on the way to work" visits are in the morning, "on the way home" in the late afternoon
- [ ] "during work" visits are at shops near where those members work
- [ ] "near home" visits cluster on weekends and evenings — and at the shop nearest home
- [ ] pick University Hill: "near home" visits (students) drop in the summer months
- [ ] pick Westcott: "near home" orders have the long tail of big weekend brunch totals
- [ ] nothing is "on the way to work" for a member who has no Work

If a chart surprises you, find a visit that looks wrong and ask why your rules labeled it
that way.

### Step 5 — Commit and get early feedback

Commit, push, and submit to GraderThan ([Reference #13](#13-how-do-i-submit-for-grading--and-review-my-feedback--with-graderthan)).
The unit tests and the classifier test tell you whether Parts 1 and 2 are right before
you build on them.

### Step 6 — Part 3: the tables (`analysis.py`)

Each function returns the small table one chart needs. `busy_table` and `reason_table` are
`pivot_table`s; `monthly_sales` is a `groupby` (by shop, or by any column you name, such as `reason`); `members_by_zip` and `demand_by_zip` count
ZIPs; `site_scores` puts it all together ([About the data](#from-reasons-to-a-place)).

### Step 7 — Part 3: the charts (`charts.py`)

Every chart is built by a function that **returns** it — a matplotlib Figure, a Plotly
Figure, or a Folium Map — so the dashboard stays short and the tests can look inside
([Reference #4](#4-how-do-i-make-a-heatmap-and-a-violin-plot-with-seaborn)–[#7](#7-how-do-i-make-a-choropleth)).

### Step 8 — Part 4: the dashboard (`dashboard.py`)

Follow the numbered comments in the file. Run it ([Reference #9](#9-how-do-i-run-the-dashboard))
and read your own charts: Is Armory Square busy when you expect? What does the violin say
about Westcott on weekends? Then look at the last tab. **Where members live** and **where
members are when they buy** are different maps. Which one should decide where shop #4 goes?

### Step 9 — Commit

### Step 10 — Reflection, then final submit

Write `code/reflection.txt` ([reflection.md](reflection.md) explains what makes a good
one), commit, push, and submit.

---

## Reference — How do I…?

### 1. How do I set up my API key?

The scorer is on the same CENT portal as Assignment 06, so it uses the same key. Create a
file named `.env` at the root of the repository, one line:

```
CENT_API_KEY=your-key-here
```

`.env` is in `.gitignore` — git will not commit it. A Codespaces secret named
`CENT_API_KEY` works too. Your key is on the portal's Home page
(https://portal.app.cent-su.org).

### 2. How do I do a spatial join with GeoPandas?

A **GeoDataFrame** is a DataFrame with a `geometry` column — points, lines or polygons.
Make points from latitude/longitude columns (x is **longitude**, y is latitude), then ask
which polygon each point is *within*:

```python
points = gpd.GeoDataFrame(rows, geometry=gpd.points_from_xy(rows["home_lon"], rows["home_lat"]),
                          crs="EPSG:4326")
joined = gpd.sjoin(points, zips[["zip", "geometry"]], how="left", predicate="within")
joined["zip"]          # the ZIP each point is in (NaN when it's in none)
```

A **CRS** (coordinate reference system) says what the numbers mean. `EPSG:4326` is
latitude/longitude in degrees — fine for a join, wrong for areas, lengths and centers,
because a degree of longitude is shorter than a degree of latitude. For those, **project**
to meters first: `zips.to_crs("EPSG:32618")` (UTM zone 18N, which covers Syracuse), then
`.centroid`, then `.to_crs("EPSG:4326")` to get back to latitude/longitude.

### 3. How do I measure distance and detour?

`haversine_km` (provided, in `geo.py`) gives the straight-line distance in kilometers
between two points — on single numbers or on whole columns at once:

```python
visits["d_home"] = haversine_km(visits["home_lat"], visits["home_lon"],
                                visits["shop_lat"], visits["shop_lon"])
```

The **detour** is how far out of the way the shop is:
`d_home + d_work − (home to work)`. On the straight line between home and work, it's 0.

### 4. How do I make a heatmap and a violin plot with seaborn?

Make the figure and axes yourself, draw on the axes, and **return the figure**:

```python
fig, ax = plt.subplots(figsize=(11, 3.6))
sns.heatmap(table, ax=ax, cmap="YlOrBr", linewidths=0.5)    # one cell per value
sns.violinplot(data=orders, x="shop", y="total", ax=ax, cut=0)
```

A **heatmap** shows a table as colors — patterns across two dimensions (day × hour) jump
out. A **violin** shows the whole *distribution* of a number for each group: where values
pile up, how spread out they are, and whether there are two bumps instead of one.

In Streamlit, `st.pyplot(fig)` draws a matplotlib Figure; `close(fig)` (in `charts.py`)
frees it afterward.

### 5. How do I make an interactive chart with Plotly?

```python
fig = px.line(monthly, x="month", y="sales", color="shop", markers=True, title="...")
st.plotly_chart(fig)
```

`color=` makes one line (a **trace**) per shop. Hover, zoom and the legend come free.

### 6. How do I put things on a map with Folium?

```python
fmap = folium.Map(location=[43.06, -76.14], zoom_start=12)
folium.Marker([lat, lon], tooltip="Home", icon=folium.Icon(color="green", icon="home")).add_to(fmap)
folium.CircleMarker([lat, lon], radius=12, color="green", fill=True, popup="...").add_to(fmap)
```

Locations are `[latitude, longitude]` — the opposite order from GeoPandas' x/y. A
`tooltip` shows on hover, a `popup` on click. In Streamlit, show the map with
`st_folium(fmap, height=450, use_container_width=True, returned_objects=[], key="...")`
(from `streamlit_folium`); `returned_objects=[]` stops the page from rerunning every time
someone pans the map.

### 7. How do I make a choropleth?

A **choropleth** fills each area by a value. Plotly needs the polygons as **GeoJSON** and a
way to match each row to a polygon:

```python
fig = px.choropleth_map(values, geojson=zips.__geo_interface__, locations="zip",
                        featureidkey="properties.zip", color="members",
                        map_style="open-street-map", center={"lat": 43.06, "lon": -76.14},
                        zoom=9.5, opacity=0.75)
```

`locations` is the column in your table; `featureidkey` is where the same value lives in
each GeoJSON polygon (`properties.zip`). `zips.__geo_interface__` turns a GeoDataFrame into
GeoJSON. Add points on top with `fig.add_scattermap(lat=..., lon=..., mode="markers")`.

### 8. How do I check my classifier?

`python code/check_score.py` from the repository root. Read
[The survey — and the scorer](#the-survey--and-the-scorer) for what the numbers mean. The
classifier test in `test_pipeline.py` uses the same scorer, so running the tests uses a
check too — but only when your reasons have changed.

### 9. How do I run the dashboard?

Open **`code/dashboard.py`** and use **Run and Debug → Streamlit Run: Current File**, or
`streamlit run code/dashboard.py` from the repository root. The first load takes a few
seconds (a year of orders); after that `pipeline.run()` is cached. If you change your
classifier while the app is running, use **⋮ → Clear cache** and rerun.

### 10. How do I debug a step?

Run `code/explore.py` with **Python Debugger: Current File**, with a breakpoint inside the
function you are writing. It runs every step on the real data and prints the first rows
of each table.

### 11. How do I run automated tests?

**Testing** panel (View → Testing) → ▶. Or from a terminal at the repository root:

```
pytest tests/test_unit.py -v
pytest tests/test_pipeline.py -k classifier     # one at a time
pytest tests/test_code.py -v
```

If the Testing panel shows no tests at all, `saltcity/__init__.py` cannot import a
function — a deleted or misspelled function name. Scroll up to the `ImportError`.

### 12. How do I commit and push?

View → Source Control → message → **Commit**, then **Sync Changes**. `.env` and `cache/`
are not committed (`.gitignore` hides them).

### 13. How do I submit for grading — and review my feedback — with GraderThan?

1. Go to **https://graderthan.cent-su.org** and log in with your SU Microsoft account.
2. Click this assignment on **Your dashboard**.
3. First time only: **Profile → Connect GitHub**.
4. Under **Request grading**, submit your fork's URL. **Commit and push first.**

The grader scores your classifier on **every** visit, not just the survey — rules that make
sense do as well there as on the survey; rules tuned to the survey's quirks don't.

### 14. How do I check my code style?

The **Code style & readability** point is four checks on everything in `code/`, and
**all four** must pass:

| check | how to see it yourself |
| --- | --- |
| no `# TODO` comments left | search `code/` for `TODO` — the starter has one in every function you write |
| no leftover `pass` stubs | every `pass` the starter left where a body goes is replaced by your code |
| a docstring on every function | keep the starter's; give any helper you add its own |
| no lint errors | run `ruff check` at the repository root — **no output means it passes** |

`ruff check` reads `ruff.toml`, which holds exactly the grader's rules. On an untouched
checkout it already reports unused imports in the files you write — the names your code
is about to use. They disappear as you write it. (Don't let `ruff check --fix` delete them.)

---

## How You're Graded

GraderThan scores this assignment out of **10 points** (see `rubric.json`):

| What | Points | Judged by |
| --- | --- | --- |
| **Unit Tests** — `test_unit.py` (every function and chart on a small hand-made example; your classifier's contract and six textbook visits) | 2 | automated tests |
| **Pipeline & App Tests** — `test_pipeline.py` (the whole year: your classifier against the survey — 85% overall, 60% per reason — the tables, the decision, and the dashboard) | 3 | automated tests |
| **Code Structure Tests** — `test_code.py` (a spatial join, pandas instead of loops, each chart's library, a classifier that uses time *and* place, the dashboard assembles the package) | 2 | automated tests |
| **Code style & readability** — no `# TODO`s, no leftover `pass`, a docstring on every function, `ruff check` clean ([Reference #14](#14-how-do-i-check-my-code-style)) | 1 | automated style checks |
| Reflection quality | 2 | AI reviewer |

**Only files in the `code/` folder are graded.**
