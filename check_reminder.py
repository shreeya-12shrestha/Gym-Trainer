"""Run on a schedule. Shows a reminder only when one is warranted."""

from reminders import reminder_text, nudge
from report import load

try:
    rows = load("sessions.csv")
except FileNotFoundError:
    rows = []

text = reminder_text(rows)

if text is None:
    print("no reminder needed today")
else:
    title, message = text
    method = nudge(title, message)
    print(f"reminded via {method}: {title} - {message}")