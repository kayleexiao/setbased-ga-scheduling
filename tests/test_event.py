import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.event import Event

# test different event identifiers to make sure parsing works correctly
event = Event(
    identifier="CPSC 531 LEC 01 TUT 01",
    al_required=True,
)

print("Event ID:", event.id)
print("Kind:", event.kind)
print("Program Code:", event.program_code)
print("Course No:", event.course_no)
print("Section Label:", event.section_label)
print("Tutorial Label:", event.tutorial_label)
print("AL Required:", event.al_required)
print("Is Evening:", event.is_evening_event)
print("Is 500 Course:", event.is_500_course)
print("Is Special Tut:", event.is_special_tut)
print("\nFull Event:", event)