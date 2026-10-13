"""
check_score.py — how well do your rules agree with the survey?  *(Provided.)*

From the repository root:

    python code/check_score.py

It builds the visits, runs your classify_visits and sends the reasons to the
scorer (see saltcity/scorer.py), then prints the answer. Sending the same reasons
again is free (cached); each new set of reasons uses one of your daily checks.
"""

from pipeline import build
from saltcity import report, score

if __name__ == "__main__":
    visits = build()["visits"]
    print(f"Sending {len(visits):,} visits to the scorer...")
    print(report(score(visits)))
