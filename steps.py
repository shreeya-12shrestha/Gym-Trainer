"""Step counting from ankle positions.

Counts alternating foot lifts, so it works for walking or marching on the
spot in front of the camera. It cannot track distance travelled - that needs
GPS or an accelerometer, not a fixed camera.

Pure logic: takes numbers in, returns numbers out, so it can be tested with
synthetic signals and no webcam.
"""


class StepCounter:
    """A step is counted each time the raised foot changes.

    lift_ratio is the minimum ankle separation needed to call a foot raised,
    expressed as a fraction of leg length. Scaling by leg length means the
    same setting works whether you stand two metres or four from the camera.
    """

    def __init__(self, lift_ratio=0.08):
        self.lift_ratio = lift_ratio
        self.state = "neutral"
        self.steps = 0

    def update(self, left_ankle_y, right_ankle_y, leg_length_px):
        """Feed one frame. Returns 1 if this frame completed a step, else 0."""
        if leg_length_px <= 0:
            return 0

        threshold = self.lift_ratio * leg_length_px
        diff = left_ankle_y - right_ankle_y     # y grows down, so negative
                                                # means the LEFT foot is higher

        if diff < -threshold:
            if self.state != "left_up":
                self.state = "left_up"
                self.steps += 1
                return 1
        elif diff > threshold:
            if self.state != "right_up":
                self.state = "right_up"
                self.steps += 1
                return 1

        return 0

    def reset(self):
        self.state = "neutral"
        self.steps = 0