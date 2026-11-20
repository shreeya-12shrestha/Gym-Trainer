import os
from session import SessionLog

TEST_FILE = "test_sessions.csv"

if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

reps = SessionLog(TEST_FILE, exercise="squat", kind="rep")
reps.log(1, 92.0, "GOOD (92)", 0.88)
reps.log(2, 131.0, "SHALLOW (131)", 0.81)
reps.close()

holds = SessionLog(TEST_FILE, exercise="plank", kind="hold")
holds.log(1, 34.0, "HOLD 34s", 0.90)
holds.close()

walks = SessionLog(TEST_FILE, exercise="walk", kind="steps")
walks.log(1, 120, "WALK 120 steps", 0.77)
walks.close()

print(open(TEST_FILE, encoding="utf-8").read())