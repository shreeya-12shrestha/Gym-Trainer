import os
from session import SessionLog
from report import load, summarise

TEST_FILE = "test_sessions.csv"

if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

log = SessionLog(TEST_FILE)
log.log_rep(1, 92.0, "GOOD DEPTH (92)", 0.88)
log.log_rep(2, 88.4, "GOOD DEPTH (88)", 0.85)
log.log_rep(3, 131.0, "TOO SHALLOW (131)", 0.81)
log.log_rep(4, 97.2, "GOOD DEPTH (97)", 0.79)
log.close()

summarise(load(TEST_FILE))