import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.schedule import Schedule
from model.extension_rules import crossover, purge, mutate_evening, mutate_AL, mutate_lecture, mutate_tutorial
from parser.slot import *
from parser.event import Event

# create some sample events
e1 = Event(
    identifier="CPSC 531 LEC 01 TUT 01",
    al_required=True,
)
e2 = Event(
    identifier="CPSC 551 LEC 01 TUT 01",
    al_required=True,
)
e3 = Event(
    identifier="CPSC 541 LEC 01 TUT 01",
    al_required=True,
)
e4 = Event(
    identifier="CPSC 531 LEC 01",
    al_required=True,
)
e5 = Event(
    identifier="CPSC 551 LEC 01",
    al_required=True,
)
e6 = Event(
    identifier="CPSC 541 LEC 01",
    al_required=True,
)

lec1 = LectureSlot(
    day="MO",
    start_time="09:00",
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2
)
lec2 = LectureSlot(
    day="TU",
    start_time="19:00",
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2
)
lec3 = LectureSlot(
    day="MO",
    start_time="15:00",
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2
)
tut1 = TutorialSlot(
    day="MO",
    start_time="08:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)
tut2 = TutorialSlot(
    day="TU",
    start_time="19:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)
tut3 = TutorialSlot(
    day="FR",
    start_time="12:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)
tut4 = TutorialSlot(
    day="TU",
    start_time="18:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)
tut5 = TutorialSlot(
    day="FR",
    start_time="9:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)
tut6 = TutorialSlot(
    day="MO",
    start_time="02:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)

slots = [lec1, lec2, lec3, tut1, tut2, tut3, tut4, tut5, tut6]
schedule = Schedule({e1: tut1, e2: tut2, e3: tut3, e4: lec1, e5: lec2, e6: lec3})

# Test purge
print("======================= Testing purge =======================")
pop = [
    (Schedule({e1: tut2, e2: tut1}), 0.2),
    (Schedule({e1: tut6, e2: tut4}), 0.9),
    (Schedule({e1: tut5, e2: tut3}), 0.5),
    (Schedule({e1: tut3, e2: tut5}), 0.3),
    (Schedule({e1: tut4, e2: tut6}), 0.6),
    (Schedule({e1: tut1, e2: tut2}), 0.78)
]

print(f"Population before purge")
for sch, fit in pop:
    print(f"  Fitness: {fit}")

remaining = purge(pop, 2)
print(f"\nPopulation after purge")
for sch, fit in remaining:
    print(f"  Fitness: {fit}")
