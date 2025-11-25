import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.event import Event
from parser.slot import LectureSlot
from model.schedule import Schedule

lec_slot = LectureSlot(
    day="MO",
    start_time="09:00",
    lecture_max=5,
    lecture_min=0,
    al_lecture_max=2
)

event = Event(
    identifier="CPSC 231 LEC 01",
    al_required=True
)

# create schedule with one assignment
sch = Schedule(assignments={event: lec_slot})

print("\nCreated Schedule:")
print(sch)

assert event in sch.assignments
assert sch.assignments[event] == lec_slot