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
    by_day = defaultdict(list)
    for r in rows:
        by_day[r["timestamp"][:10]].append(r)

    header = f"{'date':<12}{'reps':>6}{'best':>7}{'avg':>7}"
    if BODY_WEIGHT_KG:
        header += f"{'~kcal':>8}"
    print(header + "  quality")
    print("-" * 60)

    for day in sorted(by_day):
        reps = by_day[day]
        depths = [float(r["min_angle"]) for r in reps]
        good = sum(1 for r in reps if r["verdict"].startswith("GOOD"))
        line = (f"{day:<12}{len(reps):>6}{min(depths):>7.0f}"
                f"{sum(depths) / len(depths):>7.0f}")
        if BODY_WEIGHT_KG:
            kcal = estimate_kcal([r["timestamp"] for r in reps],
                                 BODY_WEIGHT_KG, EFFORT)
            line += f"{kcal:>8.0f}"
        print(line + f"  {good}/{len(reps)} good depth")

    all_depths = [float(r["min_angle"]) for r in rows]
    print("-" * 60)
    print(f"total {len(rows)} reps, best depth {min(all_depths):.0f} degrees")
    if BODY_WEIGHT_KG:
        print("kcal figures are rough estimates from published MET values")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sessions.csv"
    try:
        summarise(load(path))
    except FileNotFoundError:
        print(f"no log yet at {path}")