import time
import cv2
import numpy as np
import mediapipe as mp
from collections import deque

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

MIN_VISIBILITY = 0.3
SMOOTH_WINDOW = 5
SIDE_SWITCH_MARGIN = 0.15
MODEL_COMPLEXITY = 1

# --- your thresholds, measured from your own body ---
DOWN_ENTER = 150     # below this = a rep has started
UP_ENTER   = 165     # above this = standing again, rep over
GOOD_DEPTH = 100     # bottom at or under this = proper depth
OK_DEPTH   = 125     # between GOOD and this = almost


def to_px(landmark, w, h):
    return [landmark.x * w, landmark.y * h]


def leg_visibility(lm, hip_i, knee_i, ankle_i):
    return min(lm[hip_i].visibility,
               lm[knee_i].visibility,
               lm[ankle_i].visibility)


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle


pose = mp_pose.Pose(model_complexity=MODEL_COMPLEXITY,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
print(f"capture: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}"
      f"x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

angle_history = deque(maxlen=SMOOTH_WINDOW)
current_side = "L"
stage = "up"
reps = 0
rejected = 0
rep_min = 999
rep_valid = True
verdict = ""
verdict_colour = (255, 255, 255)
frames = 0
t0 = time.time()

while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break
    frames += 1

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    info = "NO PERSON"

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks,
                               mp_pose.POSE_CONNECTIONS)

        h, w, _ = frame.shape
        lm = results.pose_landmarks.landmark
        L = mp_pose.PoseLandmark

        visL = leg_visibility(lm, L.LEFT_HIP, L.LEFT_KNEE, L.LEFT_ANKLE)
        visR = leg_visibility(lm, L.RIGHT_HIP, L.RIGHT_KNEE, L.RIGHT_ANKLE)

        if current_side == "L" and visR > visL + SIDE_SWITCH_MARGIN:
            current_side = "R"
            angle_history.clear()
        elif current_side == "R" and visL > visR + SIDE_SWITCH_MARGIN:
            current_side = "L"
            angle_history.clear()

        if current_side == "L":
            vis = visL
            hip_i, knee_i, ankle_i = L.LEFT_HIP, L.LEFT_KNEE, L.LEFT_ANKLE
        else:
            vis = visR
            hip_i, knee_i, ankle_i = L.RIGHT_HIP, L.RIGHT_KNEE, L.RIGHT_ANKLE

        if vis < MIN_VISIBILITY:
            angle_history.clear()
            rep_valid = False            # this rep can't be trusted
            info = f"TRACKING LOST  vis {vis:.2f}"
        else:
            hip   = to_px(lm[hip_i], w, h)
            knee  = to_px(lm[knee_i], w, h)
            ankle = to_px(lm[ankle_i], w, h)

            angle_history.append(calculate_angle(hip, knee, ankle))

            if len(angle_history) == SMOOTH_WINDOW:
                knee_angle = float(np.median(angle_history))
                info = f"KNEE {int(knee_angle)}   vis {vis:.2f}"

                # ---- the rep state machine ----
                if stage == "up" and knee_angle < DOWN_ENTER:
                    stage = "down"
                    rep_min = knee_angle
                    rep_valid = True
                elif stage == "down":
                    rep_min = min(rep_min, knee_angle)
                    if knee_angle > UP_ENTER:
                        stage = "up"
                        if not rep_valid:
                            rejected += 1
                            verdict = "NOT COUNTED - tracking lost"
                            verdict_colour = (0, 0, 255)
                        else:
                            reps += 1
                            if rep_min <= GOOD_DEPTH:
                                verdict = f"GOOD DEPTH ({int(rep_min)})"
                                verdict_colour = (0, 255, 0)
                            elif rep_min <= OK_DEPTH:
                                verdict = f"ALMOST - deeper ({int(rep_min)})"
                                verdict_colour = (0, 255, 255)
                            else:
                                verdict = f"TOO SHALLOW ({int(rep_min)})"
                                verdict_colour = (0, 165, 255)
                        print(f"rep end: min={int(rep_min)}  {verdict}")

    cv2.putText(frame, f"REPS {reps}", (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3)
    cv2.putText(frame, verdict, (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, verdict_colour, 2)
    cv2.putText(frame, info, (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv2.putText(frame, f"stage: {stage}", (20, 185),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2)

    cv2.imshow("Gym Trainer - reps", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\nReps counted:  {reps}")
print(f"Reps rejected: {rejected}")
print(f"Avg FPS:       {frames / time.time() - t0:.1f}"
      if False else f"Avg FPS:       {frames / (time.time() - t0):.1f}")