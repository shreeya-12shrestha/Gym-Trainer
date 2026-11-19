"""Pure geometry. No camera, no MediaPipe, so it can be tested directly."""

import numpy as np


def to_px(landmark, w, h):
    """MediaPipe gives x as a fraction of width, y as a fraction of height.
    Convert to pixels before any angle maths, or the non-square frame
    distorts the result."""
    return [landmark.x * w, landmark.y * h]


def calculate_angle(a, b, c):
    """Angle at point b, between the lines b->a and b->c, in degrees."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle
def side_of_line(a, b, c):
    """Which side of the line a->c does point b lie on?

    Returns a signed value: positive when b is BELOW the line, negative when
    above, zero when collinear. In image coordinates y grows downward, which
    is why "below" is the positive case.

    Used to tell a sagging plank (hips below the shoulder-knee line) from a
    piked one (hips above it) - the angle at the hip is the same for both.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    return (cx - ax) * (by - ay) - (cy - ay) * (bx - ax)