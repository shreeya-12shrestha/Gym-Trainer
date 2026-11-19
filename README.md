# Gym Trainer — Computer Vision Squat Form Checker

A real-time form checker for bodyweight exercises. A webcam tracks the body,
the knee angle is computed from pose landmarks, and the system counts reps
and gives spoken feedback when depth is wrong.

Final-year major project, BE Computer Engineering, Kathmandu Engineering College.

## Current status

Working:
- Squat, lunge and push-up defined as data; only the squat thresholds are calibrated against measured angles so far
- Live pose tracking and knee-angle measurement (squat)
- Rep counting with a state machine
- Depth classification: good / almost / too shallow
- Spoken feedback and tone cues
- Per-rep confidence reporting

In progress:
- Camera placement is still sensitive; tracking can stall mid-descent when the
  lens is too low and the thighs occlude the shins
- Additional exercises (lunge, plank)

## How to run

Requires Python 3.10–3.12 on Windows.

```
py -3.10 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.py config.py      # then edit your body weight
```

```
python pose_test.py                        # squat, webcam
python pose_test.py --exercise pushup
python pose_test.py --video squats.mp4     # run against a recording
python report.py                           # progress summary from the log
```

Tests, none of which need a camera:

```
python test_angles.py
python test_exercises.py
python test_calories.py
```

Stand side-on to the camera, full body in frame, lens at roughly hip height.
Press `q` to quit.

## Design decisions

**Rule-based, not a trained classifier.** Depth is judged by joint geometry
rather than a learned model. The thresholds were measured on my own squats
(standing ~175°, full depth ~85°), which makes the logic inspectable and
explainable rather than a black box.

**Landmarks converted to pixels before any angle maths.** MediaPipe returns `x`
as a fraction of frame width and `y` as a fraction of frame height. Because the
frame is not square, feeding those fractions straight into the angle calculation
distorts the result. `angles.to_px` converts first.

**Median smoothing, not mean.** Pose estimation produces occasional impossible
single-frame readings. A median over a short window discards outliers entirely,
where a mean would be dragged by them.

**The better-visible leg is used.** In a side view one leg occludes the other,
so both legs are scored by landmark visibility each frame and the clearer one is
measured.

**Hysteresis on leg selection.** When both legs score almost equally, a plain
comparison flips between them frame to frame, and each flip corrupts the angle
mid-rep. The current leg is kept unless the other is clearly better by a margin.

**Implausible angles are rejected.** A knee angle below 35° is not physically
reachable in a bodyweight squat, so such frames are treated as tracking failure
rather than as a very deep rep.

**Reps report their own confidence.** If landmark visibility drops during a rep,
the rep is reported as unmeasured instead of being counted. A system that admits
it could not see is more useful than one that silently miscounts.

**Audio runs on a background thread.** Speech synthesis blocks for about a
second, which would freeze the video loop. Cues are queued and spoken by a
worker thread, with a per-cue cooldown so a repeated warning cannot flood the
output.

## Known limitations

- Audio uses `winsound` and Windows SAPI, so the feedback layer is Windows-only
- Single camera, side view only; depth cannot be judged from a frontal view
- Camera height and room lighting materially affect tracking reliability
- Squat only at present

## Planned

- Lunge and plank form rules
- Session logging and a progress tracker
- Calorie estimation
- Walk/run tracking with a step counter
- Workout recommendations

## Project structure

```
angles.py           pure geometry, imports nothing from MediaPipe or OpenCV
exercises.py        exercise definitions and depth grading, expressed as data
coach.py            non-blocking voice and tone feedback
session.py          per-rep CSV logging
calories.py         MET-based energy estimation from the rep log
report.py           progress summary across sessions
pose_test.py        capture loop and rep state machine
config.example.py   template for local settings (config.py is gitignored)
test_*.py           unit tests, all camera-free
```
## Acknowledgements

Pose estimation uses Google MediaPipe. All form-assessment logic, thresholds and
feedback design are my own.