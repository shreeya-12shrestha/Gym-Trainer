from calories import kcal_per_minute, active_minutes, estimate_kcal, MET

# 60 kg at 3.0 MET -> 3.0 * 3.5 * 60 / 200 = 3.15 kcal/min
got = kcal_per_minute(MET["bodyweight_general"], 60)
print(f"{'PASS' if abs(got - 3.15) < 0.01 else 'FAIL'}  kcal/min = {got:.2f}")

# five reps 4 s apart -> 3 s for the first + 4 gaps of 4 s = 19 s
stamps = [f"2026-11-19T10:00:{s:02d}" for s in (0, 4, 8, 12, 16)]
mins = active_minutes(stamps)
print(f"{'PASS' if abs(mins * 60 - 19) < 0.1 else 'FAIL'}  "
      f"active = {mins * 60:.0f} s")

# a two-minute rest must NOT be counted as exercise
stamps = ["2026-11-19T10:00:00", "2026-11-19T10:02:00"]
mins = active_minutes(stamps)
print(f"{'PASS' if abs(mins * 60 - 6) < 0.1 else 'FAIL'}  "
      f"rest excluded, active = {mins * 60:.0f} s")

print(f"\nestimate for those reps: "
      f"{estimate_kcal(stamps, 60):.2f} kcal")