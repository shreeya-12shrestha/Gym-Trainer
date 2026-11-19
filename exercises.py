"""Exercise definitions as data.

Deliberately imports nothing from MediaPipe or OpenCV. Joints are named as
plain strings and the capture loop maps them to landmarks, which means this
file and its rules can be unit tested with no camera involved.

Angles are measured at the MIDDLE joint of the three listed.

Two kinds of exercise:
  Exercise      judged by reps and depth      (squat, lunge, push-up)
  HoldExercise  judged by how long it's held  (plank)
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
    mode: str = "rep"


@dataclass(frozen=True)
class HoldExercise:
    """An exercise judged by how long a position is held, not by reps."""
    name: str
    joints: tuple
    cue_good: str
    cue_sag: str
    cue_pike: str
    straight_min: float = 165    # at or above this, the body is straight
    target_seconds: float = 30
    min_plausible: float = 60
    mode: str = "hold"

@dataclass(frozen=True)
class StepExercise:
    """Walking or marching on the spot, counted in steps rather than reps."""
    name: str
    joints: tuple = ("HIP", "KNEE", "ANKLE")   # hip and ankle give leg length
    lift_ratio: float = 0.08
    target_steps: int = 100
    min_plausible: float = 0.0
    mode: str = "steps"
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
        "walk": StepExercise(name="walk"),
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
    "plank": HoldExercise(
        name="plank",
        joints=("SHOULDER", "HIP", "KNEE"),
        cue_good="Good plank, hold it",
        cue_sag="Hips are dropping, lift them",
        cue_pike="Hips too high, lower them",
        straight_min=165,
        target_seconds=30,
    ),
}


def grade(exercise, min_angle):
    """Judge a completed rep. Returns (label, spoken cue)."""
    if min_angle <= exercise.good_depth:
        return "GOOD", exercise.cue_good
    if min_angle <= exercise.ok_depth:
        return "ALMOST", exercise.cue_almost
    return "SHALLOW", exercise.cue_shallow


def grade_hold(exercise, angle, hip_side):
    """Judge a held position. Returns (label, spoken cue).

    angle:    the angle at the middle joint
    hip_side: side_of_line(proximal, middle, distal) - positive means the
              middle joint has dropped below the line between the other two
    """
    if angle >= exercise.straight_min:
        return "GOOD", exercise.cue_good
    if hip_side > 0:
        return "SAG", exercise.cue_sag
    return "PIKE", exercise.cue_pike