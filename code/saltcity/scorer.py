"""
scorer.py — check your classifier against the survey.  *(Provided.)*

The marketing team surveyed members ("What brought you in today?") and keeps the
answers on the CENT portal. You never see them. You send a reason for EVERY
order; the portal compares the ones it has answers for and sends back how well
your rules agree:

    POST https://portal.app.cent-su.org/api/score/salt-city-coffee/visit-reasons
    X-API-KEY: your key
    {"predictions": [{"id": 100001, "label": "on the way to work"}, ...]}

    {"task": "salt-city-coffee/visit-reasons", "actual": 1000, "correct": 884,
     "mislabeled": 116, "agreement": 0.88,
     "labels": {"near home": {"actual": 291, "predicted": 305, "correct": 270,
                              "mislabeled": 21, "agreement": 0.93,
                              "most_confused_with": "other"}, ...}}

For each label, `actual` is how many survey visits really were that reason,
`predicted` how many times you said it, `correct` how many you got right, and
`agreement` = correct / actual. `predicted` much bigger than `actual` means that
rule catches visits it shouldn't.

You get a limited number of checks a day, so the answer for predictions you have
already sent is kept in cache/ and re-used: running the same rules twice is free.
"""

import hashlib
import json
import os

import pandas as pd
import requests

from .settings import BASE_URL, CACHE_DIR, REASONS, SCORE_TASK, get_api_key


def score(visits: pd.DataFrame, task: str = SCORE_TASK, id_col: str = "order_id",
          label_col: str = "reason") -> dict:
    """Send every row's (`id_col`, `label_col`) to the scorer; return its answer."""
    predictions = [{"id": int(i), "label": str(label)}
                   for i, label in zip(visits[id_col], visits[label_col])]
    body = {"predictions": predictions}
    key = get_api_key()
    headers = {"X-API-KEY": key}
    grader = os.environ.get("CENT_GRADER_KEY", "").strip()   # the autograder only
    if grader:
        headers["X-GRADER-KEY"] = grader
    digest = hashlib.sha256((task + key + grader + json.dumps(body, sort_keys=True))
                            .encode()).hexdigest()[:16]
    cached = os.path.join(CACHE_DIR, f"score_{digest}.json")
    if os.path.exists(cached):
        with open(cached, encoding="utf-8") as fh:
            return json.load(fh)

    try:
        response = requests.post(f"{BASE_URL}/api/score/{task}", headers=headers,
                                 json=body, timeout=120)
    except requests.ConnectionError as error:
        raise RuntimeError(
            "The scorer closed the connection before answering. Most often your API "
            "key is missing or wrong: check CENT_API_KEY in .env (README Reference "
            "#1).") from error
    if response.status_code != 200:
        raise RuntimeError(f"The scorer said {response.status_code}: {response.text}")
    result = response.json()
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cached, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    return result


def score_table(result: dict) -> pd.DataFrame:
    """The scorer's answer as a table, one row per label."""
    table = pd.DataFrame(result["labels"]).T
    order = [r for r in REASONS if r in table.index]
    table = table.reindex(order + [r for r in table.index if r not in order])
    columns = ["actual", "predicted", "correct", "mislabeled", "agreement",
               "most_confused_with"]
    return table[columns].rename_axis("label")


def report(result: dict) -> str:
    """The scorer's answer as text you can read in a terminal."""
    lines = [f"{result['task']}: {result['correct']} of {result['actual']} survey "
             f"visits agree ({result['agreement']:.0%})", ""]
    lines.append(score_table(result).to_string())
    return "\n".join(lines)
