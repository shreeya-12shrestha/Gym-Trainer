from datetime import date
from reminders import reminder_text, days_since_last

TODAY = date(2026, 11, 19)
failures = 0


def rows_on(day):
    return [{"timestamp": f"{day}T10:00:00",
             "exercise": "squat",
             "verdict": "GOOD DEPTH (90)"}]


def check(label, got, want):
    global failures
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label:<40} got {got!r}")
    if not ok:
        failures += 1


def title_for(day):
    text = reminder_text(rows_on(day), TODAY)
    return None if text is None else text[0]


check("gap counted correctly",
      days_since_last(rows_on("2026-11-15"), TODAY), 4)
check("no history -> nudge",
      reminder_text([], TODAY)[0], "Gym Trainer")
check("trained today -> silent",      title_for("2026-11-19"), None)
check("one day ago -> silent (rest)", title_for("2026-11-18"), None)
check("two days ago -> nudge",        title_for("2026-11-17"), "Time to train")
check("four days ago -> nudge",       title_for("2026-11-15"), "Time to train")
check("five days ago -> gentler",     title_for("2026-11-14"), "Still here")
check("twelve days ago -> softest",   title_for("2026-11-07"),
      "Your squats miss you")

print(f"\n{failures} failed")