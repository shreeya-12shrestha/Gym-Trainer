from exercises import EXERCISES, grade, grade_hold
import sys
failures = 0


def check(label, got, want):
    global failures
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label:<40} got {got}")
    if not ok:
        failures += 1


# ---- rep grading, at the boundaries ----
squat = EXERCISES["squat"]
check("squat 85 is good",            grade(squat, 85)[0], "GOOD")
check("squat exactly 100 is good",   grade(squat, 100)[0], "GOOD")
check("squat 101 is almost",         grade(squat, 101)[0], "ALMOST")
check("squat exactly 125 is almost", grade(squat, 125)[0], "ALMOST")
check("squat 126 is shallow",        grade(squat, 126)[0], "SHALLOW")

# ---- hold grading ----
plank = EXERCISES["plank"]
check("plank 175 is good",           grade_hold(plank, 175, 0)[0], "GOOD")
check("plank exactly 165 is good",   grade_hold(plank, 165, 0)[0], "GOOD")
check("plank 150, hips below = sag", grade_hold(plank, 150, 500)[0], "SAG")
check("plank 150, hips above = pike", grade_hold(plank, 150, -500)[0], "PIKE")

# ---- every definition must be internally sane ----
# ---- every definition must be internally sane ----
for key, ex in EXERCISES.items():
    check(f"{key}: three joints named", len(ex.joints), 3)
    check(f"{key}: has a valid mode",
          ex.mode in ("rep", "hold", "steps"), True)

    if ex.mode == "rep":
        check(f"{key}: good_depth < ok_depth",
              ex.good_depth < ex.ok_depth, True)
        check(f"{key}: ok_depth < down_enter",
              ex.ok_depth < ex.down_enter, True)
        check(f"{key}: down_enter < up_enter",
              ex.down_enter < ex.up_enter, True)
        check(f"{key}: three cues present",
              all([ex.cue_good, ex.cue_almost, ex.cue_shallow]), True)

    elif ex.mode == "hold":
        check(f"{key}: straight_min in range",
              0 < ex.straight_min <= 180, True)
        check(f"{key}: positive target time",
              ex.target_seconds > 0, True)
        check(f"{key}: three cues present",
              all([ex.cue_good, ex.cue_sag, ex.cue_pike]), True)

    else:
        check(f"{key}: lift ratio is a sane fraction",
              0 < ex.lift_ratio < 1, True)
        check(f"{key}: positive step target",
              ex.target_steps > 0, True)

print(f"\n{failures} failed")
sys.exit(1 if failures else 0)