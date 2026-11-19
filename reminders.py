"""Desktop reminders based on how long it's been since the last session.

Uses winotify for Windows toasts when available and falls back to spoken
output, so a missing dependency degrades the feature instead of killing it.
"""

from datetime import date

try:
    from winotify import Notification
    HAVE_TOAST = True
except ImportError:
    HAVE_TOAST = False


def nudge(title, message):
    """Show a reminder however this machine can. Returns the method used."""
    if HAVE_TOAST:
        Notification(app_id="Gym Trainer", title=title, msg=message).show()
        return "toast"
    try:
        import time
        from coach import Coach
        Coach(min_gap=0).say(f"{title}. {message}")
        time.sleep(4)        # the speech worker is a daemon, let it finish
        return "voice"
    except Exception:
        print(f"{title}: {message}")
        return "print"


def days_since_last(rows, today=None):
    today = today or date.today()
    if not rows:
        return None
    last = max(r["timestamp"][:10] for r in rows)
    return (today - date.fromisoformat(last)).days


def reminder_text(rows, today=None, rest_days=2):
    """Return (title, message), or None when no nudge is warranted."""
    gap = days_since_last(rows, today)

    if gap is None:
        return ("Gym Trainer", "No sessions logged yet - try 10 squats")
    if gap < rest_days:
        return None
    if gap <= 4:
        return ("Time to train", f"{gap} days since your last session")
    if gap <= 10:
        return ("Still here", f"{gap} days off - even 5 squats counts today")
    return ("Your squats miss you", f"{gap} days. No judgement. Just 5?")