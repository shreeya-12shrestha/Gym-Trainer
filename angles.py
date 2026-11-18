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