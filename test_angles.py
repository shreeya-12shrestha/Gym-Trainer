import sys
from angles import calculate_angle, side_of_line

failures = 0


def check(label, got, want, tol=0.5):
    global failures
    ok = abs(got - want) < tol
    print(f"{'PASS' if ok else 'FAIL'}  {label:<22} "
          f"expected {want:>7} got {got:7.2f}")
    if not ok:
        failures += 1


CASES = [
    ("straight leg",     (0, 0),   (0, 100), (0, 200),    180),
    ("right angle",      (0, 100), (0, 200), (100, 200),   90),
    ("45 degrees",       (0, 100), (0, 200), (100, 100),   45),
    ("45 the other way", (0, 100), (0, 200), (-100, 100),  45),
    ("deep squat-ish",   (0, 100), (0, 200), (50, 100),  26.57),
]

for name, hip, knee, ankle, expected in CASES:
    check(name, calculate_angle(hip, knee, ankle), expected)

a, b, c = (0, 100), (0, 200), (100, 150)
if abs(calculate_angle(a, b, c) - calculate_angle(c, b, a)) > 0.001:
    print("FAIL  symmetry: swapping a and c changed the answer")
    failures += 1
else:
    print("PASS  symmetry")

print()
SIDE_CASES = [
    ("hip below the line", (0, 0), (50, 10),  (100, 0),   "below"),
    ("hip above the line", (0, 0), (50, -10), (100, 0),   "above"),
    ("hip on the line",    (0, 0), (50, 0),   (100, 0),   "flat"),
    ("works when tilted",  (0, 0), (50, 60),  (100, 100), "below"),
]

for name, a, b, c, want in SIDE_CASES:
    s = side_of_line(a, b, c)
    got = "below" if s > 0 else "above" if s < 0 else "flat"
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {name:<22} "
          f"expected {want:<6} got {got}")
    if not ok:
        failures += 1

print(f"\n{failures} failed")
sys.exit(1 if failures else 0)