from angles import calculate_angle

# Each case: name, hip, knee, ankle, expected angle at the knee.
# Remember y grows DOWNWARD in image coordinates.
CASES = [
    ("straight leg",      (0, 0),   (0, 100), (0, 200),    180),
    ("right angle",       (0, 100), (0, 200), (100, 200),   90),
    ("45 degrees",        (0, 100), (0, 200), (100, 100),   45),
    ("45 the other way",  (0, 100), (0, 200), (-100, 100),  45),
    ("deep squat-ish",    (0, 100), (0, 200), (50, 100),  26.57),
]

failures = 0

for name, hip, knee, ankle, expected in CASES:
    got = calculate_angle(hip, knee, ankle)
    ok = abs(got - expected) < 0.5
    print(f"{'PASS' if ok else 'FAIL'}  {name:<18} "
          f"expected {expected:>6}  got {got:6.2f}")
    if not ok:
        failures += 1

# the angle at b must not depend on which leg we name first
a, b, c = (0, 100), (0, 200), (100, 150)
if abs(calculate_angle(a, b, c) - calculate_angle(c, b, a)) > 0.001:
    print("FAIL  symmetry: swapping a and c changed the answer")
    failures += 1
else:
    print("PASS  symmetry")

print(f"\n{len(CASES) + 1 - failures} passed, {failures} failed")