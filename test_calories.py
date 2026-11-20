import sys
from calories import kcal_per_minute, active_minutes, MET

failures = 0


def check(label, ok, detail=""):
    global failures
    print(f"{'PASS' if ok else 'FAIL'}  {label:<34} {detail}")
    if not ok:
        failures += 1


got = kcal_per_minute(MET["bodyweight_general"], 60)
check("kcal/min, 60 kg at 3.0 MET", abs(got - 3.15) < 0.01, f"= {got:.2f}")

stamps = [f"2026-11-19T10:00:{s:02d}" for s in (0, 4, 8, 12, 16)]
secs = active_minutes(stamps) * 60
check("five reps 4 s apart", abs(secs - 19) < 0.1, f"= {secs:.0f} s")

stamps = ["2026-11-19T10:00:00", "2026-11-19T10:02:00"]
secs = active_minutes(stamps) * 60
check("two minute rest excluded", abs(secs - 6) < 0.1, f"= {secs:.0f} s")

print(f"\n{failures} failed")
sys.exit(1 if failures else 0)