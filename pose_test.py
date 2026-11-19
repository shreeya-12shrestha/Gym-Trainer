import argparse
import time
from collections import deque

import cv2
import numpy as np
import mediapipe as mp

from angles import to_px, calculate_angle
from coach import Coach
from exercises import EXERCISES, grade
from session import SessionLog

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

MIN_VISIBILITY = 0.3
SMOOTH_WINDOW = 5
SIDE_SWITCH_MARGIN = 0.15
MODEL_COMPLEXITY = 1
TRUST_VIS = 0.60

parser = argparse.ArgumentParser(description="Exercise form checker")
parser.add_argument("--exercise", default="squat", choices=sorted(EXERCISES))
parser.add_argument("--video", default=None,
                    help="path to a video file; omit to use the webcam")
args = parser.parse_args()

ex = EXERCISES[args.exercise]


def joint_ids(side, joints):
    """('HIP','KNEE','ANKLE') + 'L' -> MediaPipe landmark enums."""
    prefix = "LEFT" if side == "L" else "RIGHT"
    return [getattr(mp_pose.PoseLandmark, f"{prefix}_{j}") for j in joints]


def visibility(lm, ids):
    return min(lm[i].visibility for i in ids)


LEFT_IDS = joint_ids("L", ex.joints)
RIGHT_IDS = joint_ids("R", ex.joints)

pose = mp_pose.Pose(model_complexity=MODEL_COMPLEXITY,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)

if args.video is None:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(f"webcam: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}"
          f"x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
else:
    cap = cv2.VideoCapture(args.video)
    print(f"video file: {args.video}")

print(f"exercise: {ex.name}   good <= {ex.good_depth}   "
      f"almost <= {ex.ok_depth}")

angle_history = deque(maxlen=SMOOTH_WINDOW)
current_side = "L"
stage = "up"
reps = 0
rejected = 0
rep_min = 999.0
rep_worst_vis = 1.0
rep_valid = True
verdict = ""
verdict_colour = (255, 255, 255)
frames = 0
t0 = time.time()

coach = Coach(min_gap=1.0)
session = SessionLog(exercise=ex.name)

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

        visL = visibility(lm, LEFT_IDS)
        visR = visibility(lm, RIGHT_IDS)

        if current_side == "L" and visR > visL + SIDE_SWITCH_MARGIN:
            current_side = "R"
            angle_history.clear()
        elif current_side == "R" and visL > visR + SIDE_SWITCH_MARGIN:
            current_side = "L"
            angle_history.clear()

        ids = LEFT_IDS if current_side == "L" else RIGHT_IDS
        vis = visL if current_side == "L" else visR

        if vis < MIN_VISIBILITY:
            angle_history.clear()
            rep_valid = False
            info = f"TRACKING LOST  vis {vis:.2f}"
            coach.say("I cannot see you", key="novis")
        else:
            p1, p2, p3 = (to_px(lm[i], w, h) for i in ids)
            raw_angle = calculate_angle(p1, p2, p3)

            if raw_angle < ex.min_plausible:
                info = f"IMPLAUSIBLE {int(raw_angle)} - ignored"
                rep_valid = False
            else:
                angle_history.append(raw_angle)

                if len(angle_history) == SMOOTH_WINDOW:
                    angle = float(np.median(angle_history))
                    info = f"{ex.joints[1]} {int(angle)}   vis {vis:.2f}"

                    if stage == "up" and angle < ex.down_enter:
                        stage = "down"
                        rep_min = angle
                        rep_worst_vis = vis
                        rep_valid = True
                    elif stage == "down":
                        rep_min = min(rep_min, angle)
                        rep_worst_vis = min(rep_worst_vis, vis)

                        if angle > ex.up_enter:
                            stage = "up"
                            if not rep_valid:
                                rejected += 1
                                verdict = "NOT COUNTED - tracking lost"
                                verdict_colour = (0, 0, 255)
                                coach.say("I could not see that rep",
                                          key="badrep")
                            elif rep_worst_vis < TRUST_VIS:
                                rejected += 1
                                verdict = (f"LOW CONFIDENCE - vis fell to "
                                           f"{rep_worst_vis:.2f}")
                                verdict_colour = (0, 0, 255)
                                coach.say("I could not see that rep clearly",
                                          key="badrep")
                            else:
                                reps += 1
                                label, cue = grade(ex, rep_min)
                                verdict = f"{label} ({int(rep_min)})"
                                if label == "GOOD":
                                    verdict_colour = (0, 255, 0)
                                    coach.beep(1000, 120, key="good")
                                elif label == "ALMOST":
                                    verdict_colour = (0, 255, 255)
                                else:
                                    verdict_colour = (0, 165, 255)
                                    coach.beep(400, 300, key="shallow")
                                coach.say(cue, key=label)
                                session.log_rep(reps, rep_min, verdict,
                                                rep_worst_vis)
                            print(f"rep end: min={int(rep_min)}  "
                                  f"worst_vis={rep_worst_vis:.2f}  {verdict}")

    cv2.putText(frame, f"{ex.name.upper()}  REPS {reps}", (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    cv2.putText(frame, verdict, (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, verdict_colour, 2)
    cv2.putText(frame, info, (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv2.putText(frame, f"stage: {stage}", (20, 185),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2)

    cv2.imshow(f"Gym Trainer - {ex.name}", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
session.close()

print(f"\nReps counted:  {reps}")
print(f"Reps rejected: {rejected}")
print(f"Avg FPS:       {frames / (time.time() - t0):.1f}")