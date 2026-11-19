import time
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from angles import to_px, calculate_angle
import sys
from coach import Coach
from session import SessionLog

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

MIN_VISIBILITY = 0.3
SMOOTH_WINDOW = 5
SIDE_SWITCH_MARGIN = 0.15
MODEL_COMPLEXITY = 1

DOWN_ENTER = 150
UP_ENTER   = 165
GOOD_DEPTH = 100
OK_DEPTH   = 125

MIN_PLAUSIBLE = 35      # no bodyweight squat bends the knee tighter than this
TRUST_VIS     = 0.60    # if vis fell below this mid-rep, don't trust the depth


def leg_visibility(lm, hip_i, knee_i, ankle_i):
    return min(lm[hip_i].visibility,
               lm[knee_i].visibility,
               lm[ankle_i].visibility)


pose = mp_pose.Pose(model_complexity=MODEL_COMPLEXITY,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)

SOURCE = sys.argv[1] if len(sys.argv) > 1 else None

if SOURCE is None:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(f"webcam: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}"
          f"x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
else:
    cap = cv2.VideoCapture(SOURCE)
    print(f"video file: {SOURCE}")

angle_history = deque(maxlen=SMOOTH_WINDOW)
current_side = "L"
stage = "up"
coach = Coach(min_gap=1.0)
session = SessionLog()
reps = 0
rejected = 0
rep_min = 999
rep_worst_vis = 1.0
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
            rep_valid = False
            info = f"TRACKING LOST  vis {vis:.2f}"
            coach.say("I cannot see your legs", key="novis")
        else:
            hip   = to_px(lm[hip_i], w, h)
            knee  = to_px(lm[knee_i], w, h)
            ankle = to_px(lm[ankle_i], w, h)
            raw_angle = calculate_angle(hip, knee, ankle)

            if raw_angle < MIN_PLAUSIBLE:
                # physically impossible -> treat as a bad landmark, not a squat
                info = f"IMPLAUSIBLE {int(raw_angle)} - ignored"
                rep_valid = False
            else:
                angle_history.append(raw_angle)

                if len(angle_history) == SMOOTH_WINDOW:
                    knee_angle = float(np.median(angle_history))
                    info = f"KNEE {int(knee_angle)}   vis {vis:.2f}"

                    if stage == "up" and knee_angle < DOWN_ENTER:
                        stage = "down"
                        rep_min = knee_angle
                        rep_worst_vis = vis
                        rep_valid = True
                    elif stage == "down":
                        rep_min = min(rep_min, knee_angle)
                        rep_worst_vis = min(rep_worst_vis, vis)

                        if knee_angle > UP_ENTER:
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
                            elif rep_min <= GOOD_DEPTH:
                                reps += 1
                                verdict = f"GOOD DEPTH ({int(rep_min)})"
                                verdict_colour = (0, 255, 0)
                                coach.beep(1000, 120, key="good")
                                coach.say("Good rep", key="goodsay")
                            elif rep_min <= OK_DEPTH:
                                reps += 1
                                verdict = f"ALMOST - deeper ({int(rep_min)})"
                                verdict_colour = (0, 255, 255)
                                coach.say("Almost, go a little deeper",
                                          key="almost")
                            else:
                                reps += 1
                                verdict = f"TOO SHALLOW ({int(rep_min)})"
                                verdict_colour = (0, 165, 255)
                                coach.beep(400, 300, key="shallow")
                                coach.say("Too shallow, go deeper",
                                          key="shallow")
                            print(f"rep end: min={int(rep_min)}  "
                                  f"worst_vis={rep_worst_vis:.2f}  {verdict}")
                            session.log_rep(reps, rep_min, verdict,
                                            rep_worst_vis)
                                  

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
session.close()

print(f"\nReps counted:  {reps}")
print(f"Reps rejected: {rejected}")
print(f"Avg FPS:       {frames / (time.time() - t0):.1f}")