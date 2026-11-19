import csv
import os
from datetime import datetime

FIELDS = ["timestamp", "exercise", "rep", "min_angle", "verdict", "confidence"]


class SessionLog:
    """Appends one row per completed rep to a CSV."""

    def __init__(self, path="sessions.csv", exercise="squat"):
        self.path = path
        self.exercise = exercise
        is_new = not os.path.exists(path)
        self._fh = open(path, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fh, fieldnames=FIELDS)
        if is_new:
            self._writer.writeheader()

    def log_rep(self, rep_number, min_angle, verdict, confidence):
        self._writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "exercise": self.exercise,
            "rep": rep_number,
            "min_angle": round(float(min_angle), 1),
            "verdict": verdict,
            "confidence": round(float(confidence), 2),
        })
        self._fh.flush()     # flush per rep: a crash mid-workout loses nothing

    def close(self):
        self._fh.close()