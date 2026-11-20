import csv
import sys
from collections import defaultdict

from calories import estimate_kcal

try:
    from config import BODY_WEIGHT_KG, EFFORT
except ImportError:
    BODY_WEIGHT_KG, EFFORT = None, "bodyweight_general"


def load(path="sessions.csv"):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def summarise(rows):
    by_day = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_day[r["timestamp"][:10]][(r["exercise"], r["kind"])].append(r)

    for day in sorted(by_day):
        print(day)
        for (exercise, kind), items in sorted(by_day[day].items()):
            metrics = [float(i["metric"]) for i in items]

            if kind == "rep":
                good = sum(1 for i in items
                           if i["verdict"].startswith("GOOD"))
                line = (f"  {exercise:<8} {len(items):>3} reps    "
                        f"best {min(metrics):>3.0f}deg   "
                        f"avg {sum(metrics) / len(metrics):>3.0f}deg   "
                        f"{good}/{len(items)} good")
                if BODY_WEIGHT_KG:
                    kcal = estimate_kcal([i["timestamp"] for i in items],
                                         BODY_WEIGHT_KG, EFFORT)
                    line += f"   ~{kcal:.0f} kcal"
                print(line)

            elif kind == "hold":
                print(f"  {exercise:<8} {len(items):>3} holds   "
                      f"longest {max(metrics):>3.0f}s   "
                      f"total {sum(metrics):>4.0f}s")

            else:
                print(f"  {exercise:<8} {sum(metrics):>5.0f} steps")

    rep_metrics = [float(r["metric"]) for r in rows if r["kind"] == "rep"]
    print()
    if rep_metrics:
        print(f"total {len(rep_metrics)} reps, "
              f"best depth {min(rep_metrics):.0f} degrees")
    if BODY_WEIGHT_KG:
        print("kcal figures are rough estimates from published MET values")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sessions.csv"
    try:
        summarise(load(path))
    except FileNotFoundError:
        print(f"no log yet at {path}")