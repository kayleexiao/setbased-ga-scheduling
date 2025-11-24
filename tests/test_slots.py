from src.model.lecture_slot import LectureSlot
from src.model.tutorial_slot import TutorialSlot

lec = LectureSlot(
    slot_key=("LEC", "MO", "09:00"),
    kind="LEC",
    day="MO",
    start_time="09:00",
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2,
    is_evening_slot=False,
    forbidden_for_lectures=False
    )

tut = TutorialSlot(
    slot_key=("TUT", "FR", "12:00"),
    kind="TUT",
    day="FR",
    start_time="12:00",
    tutorial_max=10,
    tutorial_min=1,
    al_tutorial_max=3,
    is_evening_slot=False,
    is_tth_18_19_tutorial=False
    )

print("LectureSlot:", lec)
print("TutorialSlot:", tut)