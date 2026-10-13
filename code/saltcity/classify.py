"""
classify.py — why did each visit happen?  **You design this one.**

Every visit gets one of the five reasons in settings.REASONS:

    on the way to work   stopped on the trip from home to work
    during work          a break from work, near work
    on the way home      stopped on the trip from work to home
    near home            near where they live (weekends, mornings off, evenings)
    other                none of these: an event, shopping, visiting a friend

Nobody told us the reasons. You decide which features matter and where the
cut-offs go, then check your rules against the survey with the scorer
(`python code/check_score.py`). Look at your results on the charts, too: if
"on the way to work" visits show up at 2 p.m., your rules are off.

You start from a baseline that works: it uses only the clock. Run check_score.py
on it first. It agrees with the survey on about 76% of visits, and never says
"other" (0%). To pass you need 85% overall and 60% for every reason. Look at
what it gets wrong (most_confused_with), ask what would tell those visits apart
— usually a place, not a time: d_home, d_work, detour, has_work — change one
thing, and score again.

Keep your cut-offs in named constants at the top of this file, like these, so
they are easy to find and change.
"""

import numpy as np
import pandas as pd

from .settings import (  # noqa: F401  (OTHER: the baseline never uses it — yet)
    DURING_WORK,
    NEAR_HOME,
    ON_THE_WAY_HOME,
    ON_THE_WAY_TO_WORK,
    OTHER,
)

WORK_STARTS_BY = 10.0     # hour: weekday visits before this are the commute in
WORK_ENDS_BY = 15.5       # hour: weekday visits before this are during work
EVENING_ENDS_BY = 19.5    # hour: weekday visits before this are the commute home


def classify_visits(visits: pd.DataFrame) -> pd.DataFrame:
    """`visits` (from add_features) with a new `reason` column: one of the five
    reasons in settings.REASONS for every row.

    A new DataFrame, same rows in the same order; `visits` is not changed.

    The baseline: `np.select` checks the conditions in order and gives each row
    the reason of the first one that is true, or the default. Improve it.
    """
    result = visits.copy()
    weekday = result["weekday"]
    hour = result["hour"]
    result["reason"] = np.select(
        [
            weekday & (hour < WORK_STARTS_BY),
            weekday & (hour < WORK_ENDS_BY),
            weekday & (hour < EVENING_ENDS_BY),
        ],
        [ON_THE_WAY_TO_WORK, DURING_WORK, ON_THE_WAY_HOME],
        default=NEAR_HOME,
    )
    return result
