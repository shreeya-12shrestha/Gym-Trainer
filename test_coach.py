from coach import Coach

coach = Coach(min_gap=0.0)

print("1 beep | 2 good rep | 3 go deeper | 4 back straight | 5 can't see | q quit")

while True:
    k = input("> ").strip()
    if k == "q":
        break
    elif k == "1":
        coach.beep()
    elif k == "2":
        coach.say("Good rep")
    elif k == "3":
        coach.say("Go deeper")
    elif k == "4":
        coach.say("Keep your back straight")
    elif k == "5":
        coach.say("I cannot see your legs")