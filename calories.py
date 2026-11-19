"""Energy estimation from the rep log.

MET values from the 2024 Adult Compendium of Physical Activities:
  02056   3.0   body weight resistance exercise (squat, lunge, push-up), general
  02057   6.5   body weight resistance exercise, high intensity
  02052   5.0   resistance training, squats/deadlift, slow or explosive effort

kcal per minute = MET * 3.5 * weight_kg / 200

These are population averages measured in a lab, not a measurement of this
user. The output is an estimate with an error margin of tens of percent, and
should be presented to the user as such.
"""

from datetime import datetime

MET = {
    "bodyweight_general": 3.0,
    "bodyweight_high": 6.5,
    "loaded_squat": 5.0,
}

MAX_REP_GAP_S = 8.0     # a longer gap between reps counts as rest
DEFAULT_REP_S = 3.0     # assumed duration of one rep


def kcal_per_minute(met, weight_kg):
    return met * 3.5 * weight_kg / 200.0


def active_minutes(timestamps, max_gap_s=MAX_REP_GAP_S,
                   default_rep_s=DEFAULT_REP_S):
    """Time spent actually moving. Gaps longer than max_gap_s are rest and
    are not counted."""
    if not timestamps:
        return 0.0
    times = sorted(datetime.fromisoformat(t) for t in timestamps)
    seconds = default_rep_s                      # the first rep itself
    for earlier, later in zip(times, times[1:]):
        gap = (later - earlier).total_seconds()
        seconds += gap if gap <= max_gap_s else default_rep_s
    return seconds / 60.0


def estimate_kcal(timestamps, weight_kg, effort="bodyweight_general"):
    return kcal_per_minute(MET[effort], weight_kg) * active_minutes(timestamps)