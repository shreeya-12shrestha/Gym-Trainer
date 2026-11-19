from exercises import EXERCISES, grade

failures = 0


def check(label, got, want):
    global failures
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label:<34} got {got}")
    if not ok:
        failures += 1


squat = EXERCISES["squat"]

check("squat 85 is good",            grade(squat, 85)[0], "GOOD")
check("squat exactly 100 is good",   grade(squat, 100)[0], "GOOD")
check("squat 101 is almost",         grade(squat, 101)[0], "ALMOST")
check("squat exactly 125 is almost", grade(squat, 125)[0], "ALMOST")
check("squat 126 is shallow",        grade(squat, 126)[0], "SHALLOW")
check("squat 144 is shallow",        grade(squat, 144)[0], "SHALLOW")

# every exercise must have sane, ordered thresholds
for key, ex in EXERCISES.items():
    check(f"{key}: good_depth < ok_depth",
          ex.good_depth < ex.ok_depth, True)
    check(f"{key}: ok_depth < down_enter",
          ex.ok_depth < ex.down_enter, True)
    check(f"{key}: down_enter < up_enter",
          ex.down_enter < ex.up_enter, True)
    check(f"{key}: three joints named",
          len(ex.joints), 3)
    check(f"{key}: all three cues present",
          all([ex.cue_good, ex.cue_almost, ex.cue_shallow]), True)

print(f"\n{failures} failed")