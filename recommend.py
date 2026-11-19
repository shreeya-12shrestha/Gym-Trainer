"""Next-session suggestion from the rep log.

This is rule-based progressive overload, not a trained model. Every rule is a
stated heuristic that can be argued with, and the reason is returned alongside
the suggestion so the user is never told what to do without being told why.
"""

from collections import defaultdict
from datetime import date

GOOD_RATIO_TO_PROGRESS = 0.8     # form solid enough to add volume
GOOD_RATIO_STRUGGLING = 0.5      # form poor enough to hold volume
PROGRESS_STEP = 0.10             # +10% reps when progressing
LAYOFF_DAYS = 4                  # longer gap than this = ease back in
BASELINE_REPS = 10


def by_day(rows):
    days = defaultdict(list)
    for r in rows:
        days[r["timestamp"][:10]].append(r)
    return days


def good_ratio(reps):
    if not reps:
        return 0.0
    return sum(1 for r in reps if r["verdict"].startswith("GOOD")) / len(reps)


def recommend(rows, today=None):
    """Return (exercise, target_reps, reason). target_reps of 0 means rest."""
    today = today or date.today()

    if not rows:
        return ("squat", BASELINE_REPS,
                "no history yet, start with a baseline session")

    days = by_day(rows)
    last_day = max(days)
    last = days[last_day]

    exercise = last[-1]["exercise"]
    last_reps = len(last)
    ratio = good_ratio(last)
    gap = (today - date.fromisoformat(last_day)).days

    if gap == 0:
        return (exercise, 0, "already trained today, rest or stretch instead")

    if gap > LAYOFF_DAYS:
        return (exercise, max(BASELINE_REPS, int(last_reps * 0.7)),
                f"{gap} days since the last session, ease back in")

    if ratio < GOOD_RATIO_STRUGGLING:
        return (exercise, last_reps,
                f"only {ratio:.0%} of last session reached depth, "
                f"hold the volume and work on depth")

    if ratio >= GOOD_RATIO_TO_PROGRESS:
        return (exercise, last_reps + max(1, round(last_reps * PROGRESS_STEP)),
                f"{ratio:.0%} of last session reached depth, add volume")

    return (exercise, last_reps,
            f"{ratio:.0%} of last session reached depth, repeat the same")


if __name__ == "__main__":
    import sys
    from report import load

    path = sys.argv[1] if len(sys.argv) > 1 else "sessions.csv"
    try:
        rows = load(path)
    except FileNotFoundError:
        rows = []

    ex, target, reason = recommend(rows)
    if target == 0:
        print(f"Today: rest  -  {reason}")
    else:
        print(f"Today: {target} {ex}s  -  {reason}")