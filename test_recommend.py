from datetime import date
from recommend import recommend

TODAY = date(2026, 11, 19)
failures = 0


def session(day, verdicts, exercise="squat"):
    return [{"timestamp": f"{day}T10:00:{i:02d}",
             "exercise": exercise,
             "verdict": v} for i, v in enumerate(verdicts)]


def check(label, got, want):
    global failures
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label:<38} got {got}")
    if not ok:
        failures += 1


# no history at all
ex, reps, _ = recommend([], TODAY)
check("empty log suggests a baseline", (ex, reps), ("squat", 10))

# trained today already
rows = session("2026-11-19", ["GOOD DEPTH (90)"] * 10)
_, reps, _ = recommend(rows, TODAY)
check("same day suggests rest", reps, 0)

# perfect form yesterday -> add volume
rows = session("2026-11-18", ["GOOD DEPTH (90)"] * 10)
_, reps, _ = recommend(rows, TODAY)
check("all reps good -> more volume", reps, 11)

# poor depth yesterday -> hold volume
rows = session("2026-11-18",
              ["TOO SHALLOW (140)"] * 8 + ["GOOD DEPTH (90)"] * 2)
_, reps, _ = recommend(rows, TODAY)
check("20% good -> hold volume", reps, 10)

# middling form -> repeat
rows = session("2026-11-18",
              ["GOOD DEPTH (90)"] * 6 + ["TOO SHALLOW (140)"] * 4)
_, reps, _ = recommend(rows, TODAY)
check("60% good -> repeat the same", reps, 10)

# two weeks off -> ease back in
rows = session("2026-11-05", ["GOOD DEPTH (90)"] * 20)
_, reps, _ = recommend(rows, TODAY)
check("14 day layoff -> reduced volume", reps, 14)

# the exercise carries over from the last session
rows = session("2026-11-18", ["GOOD DEPTH (90)"] * 10, exercise="pushup")
ex, _, _ = recommend(rows, TODAY)
check("suggests the last exercise trained", ex, "pushup")

print(f"\n{failures} failed")