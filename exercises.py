"""Exercise definitions as data.

Deliberately imports nothing from MediaPipe or OpenCV. Joints are named as
plain strings and the capture loop maps them to landmarks, which means this
file and its rules can be unit tested with no camera involved.

Angles are measured at the MIDDLE joint of the three listed.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Exercise:
    name: str
    joints: tuple        # (proximal, middle, distal), without LEFT_/RIGHT_
    down_enter: float    # below this angle, a rep has begun
    up_enter: float      # above this angle, the rep is over
    good_depth: float    # bottom at or under this = correct depth
    ok_depth: float      # between good_depth and this = nearly there
    min_plausible: float # tighter than this is a tracking failure, not a rep
    cue_good: str
    cue_almost: str
    cue_shallow: str


EXERCISES = {
    # thresholds measured from my own squats: standing ~175, full depth ~85
    "squat": Exercise(
        name="squat",
        joints=("HIP", "KNEE", "ANKLE"),
        down_enter=150, up_enter=165,
        good_depth=100, ok_depth=125, min_plausible=35,
        cue_good="Good rep",
        cue_almost="Almost, go a little deeper",
        cue_shallow="Too shallow, go deeper",
    ),
    # starting estimates - to be calibrated the same way the squat was
    "lunge": Exercise(
        name="lunge",
        joints=("HIP", "KNEE", "ANKLE"),
        down_enter=150, up_enter=165,
        good_depth=95, ok_depth=115, min_plausible=35,
        cue_good="Good lunge",
        cue_almost="Drop the back knee lower",
        cue_shallow="Front knee needs to bend more",
    ),
    "pushup": Exercise(
        name="pushup",
        joints=("SHOULDER", "ELBOW", "WRIST"),
        down_enter=140, up_enter=160,
        good_depth=90, ok_depth=110, min_plausible=30,
        cue_good="Good push up",
        cue_almost="Chest a little lower",
        cue_shallow="Not deep enough, bend the elbows more",
    ),
}


def grade(exercise, min_angle):
    """Return (verdict_label, spoken_cue) for the deepest angle in a rep."""
    if min_angle <= exercise.good_depth:
        return "GOOD", exercise.cue_good
    if min_angle <= exercise.ok_depth:
        return "ALMOST", exercise.cue_almost
    return "SHALLOW", exercise.cue_shallow