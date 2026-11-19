# Gym Trainer — Computer Vision Squat Form Checker

A real-time form checker for bodyweight exercises. A webcam tracks the body,
the knee angle is computed from pose landmarks, and the system counts reps
and gives spoken feedback when depth is wrong.

Final-year major project, BE Computer Engineering, Kathmandu Engineering College.

## Current status

Working:
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

Requires Python 3.11 on Windows.

```
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python pose_test.py                 # webcam
python pose_test.py squats.mp4      # a recorded video
python test_angles.py               # unit tests, no camera needed
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
angles.py        pure geometry, no camera dependency
coach.py         non-blocking voice and tone feedback
pose_test.py     capture loop, rep state machine, feedback rules
test_angles.py   unit tests for the angle maths
```

## Acknowledgements

Pose estimation uses Google MediaPipe. All form-assessment logic, thresholds and
feedback design are my own.