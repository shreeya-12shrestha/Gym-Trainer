from steps import StepCounter
import sys

LEG = 400.0          # leg length in pixels; threshold = 0.08 * 400 = 32 px
failures = 0


def check(label, got, want):
    global failures
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label:<44} got {got}")
    if not ok:
        failures += 1


def run(diffs, leg=LEG):
    """Feed a sequence of (left_y - right_y) values, return total steps."""
    sc = StepCounter()
    for d in diffs:
        sc.update(d, 0.0, leg)      # right ankle fixed at 0, left at d
    return sc.steps


check("standing still counts nothing",
      run([0.0] * 100), 0)

check("jitter below threshold counts nothing",
      run([-20, 20, -20, 20, -20, 20] * 10), 0)

check("ten alternations count ten steps",
      run([-50, 50] * 5), 10)

check("one foot held up counts one step",
      run([-50] * 50), 1)

check("a foot must come down before counting again",
      run([-50, -50, -50, 50, 50, -50]), 3)

# scale independence: a nearer person has a longer leg in pixels, so the same
# pixel movement should NOT count the same
check("25px swing counts at leg=200",
      run([-25, 25] * 3, leg=200), 6)
check("same 25px swing ignored at leg=400",
      run([-25, 25] * 3, leg=400), 0)

check("zero leg length is handled, not crashed",
      run([-50, 50] * 5, leg=0), 0)

print(f"\n{failures} failed")
sys.exit(1 if failures else 0)