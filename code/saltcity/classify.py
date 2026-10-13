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

Start simple, score it, look at what it gets wrong (most_confused_with), change
one thing, score again. Put your cut-offs in named constants at the top of this
file, like settings.py does, so they are easy to find and change.
"""

import numpy as np  # noqa: F401  (np.select is one good way to apply rules in order)
import pandas as pd

from .settings import (  # noqa: F401  (you will use these)
    DURING_WORK,
    NEAR_HOME,
    ON_THE_WAY_HOME,
    ON_THE_WAY_TO_WORK,
    OTHER,
)


def classify_visits(visits: pd.DataFrame) -> pd.DataFrame:
    """`visits` (from add_features) with a new `reason` column: one of the five
    reasons in settings.REASONS for every row.

    A new DataFrame, same rows in the same order; `visits` is not changed.
    """
    # TODO: your code here
    pass
