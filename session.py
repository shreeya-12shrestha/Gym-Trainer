import csv
import os
from datetime import datetime

FIELDS = ["timestamp", "exercise", "kind", "index", "metric",
          "verdict", "confidence"]


class SessionLog:
    """Appends one row per completed rep, hold or walk.

    `kind` says how to read `metric`:
        rep    -> the deepest angle reached, in degrees (lower is deeper)
        hold   -> how long the position was held, in seconds
        steps  -> how many steps were counted
    """

    def __init__(self, path="sessions.csv", exercise="squat", kind="rep"):
        self.path = path
        self.exercise = exercise
        self.kind = kind
        is_new = not os.path.exists(path)
        self._fh = open(path, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fh, fieldnames=FIELDS)
        if is_new:
            self._writer.writeheader()

    def log(self, index, metric, verdict, confidence):
        self._writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "exercise": self.exercise,
            "kind": self.kind,
            "index": index,
            "metric": round(float(metric), 1),
            "verdict": verdict,
            "confidence": round(float(confidence), 2),
        })
        self._fh.flush()

    def close(self):
        self._fh.close()