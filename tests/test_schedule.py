from src.model.event import Event
from src.model.lecture_slot import LectureSlot
from src.model.schedule import Schedule

lec_slot = LectureSlot(
    slot_key=("LEC", "MO", "09:00"),
    kind="LEC",
    day="MO",
    start_time="09:00",
    is_evening_slot=False,
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2,
    forbidden_for_lectures=False
)

event = Event(
    id="CPSC 231 LEC 01",
    kind="LEC",
    program_code="CPSC",
    course_no=231,
    section_label="LEC 01",
    tutorial_label=None,
    al_required=True,
    is_evening_event=False,
    is_500_course=False,
    is_special_tut=False
)

# create schedule with one assignment
sch = Schedule(assignments={event: lec_slot})

print("\nCreated Schedule:")
print(sch)

assert event in sch.assignments
assert sch.assignments[event] == lec_slot