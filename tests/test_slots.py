import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.slot import LectureSlot, TutorialSlot
from pprint import pformat

lec = LectureSlot(
    day="MO",
    start_time="09:00",
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2
)

tut = TutorialSlot(
    day="FR",
    start_time="12:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3
)

print("LectureSlot:", lec)
print("LectureSlot slot_key:", lec.slot_key)
print("LectureSlot details:")
print(pformat({k: getattr(lec, k) for k in sorted(vars(lec).keys())}))

print("\nTutorialSlot:", tut)
print("TutorialSlot slot_key:", tut.slot_key)
print("TutorialSlot details:")
print(pformat({k: getattr(tut, k) for k in sorted(vars(tut).keys())}))
