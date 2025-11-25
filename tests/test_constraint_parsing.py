import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.parser import read_all_lines, split_into_sections
from parser.event import parse_lectures, parse_tutorials
from parser.slot import parse_lecture_slots, parse_tutorial_slots
from parser.constraint import (
    parse_not_compatible,
    parse_unwanted,
    parse_preferences,
    parse_pair,
    parse_partial_assignments
)

def check(cond, msg):
    if cond:
        print(f"PASS: {msg}")
    else:
        print(f"FAIL: {msg}")
        raise AssertionError(msg)

print("\n====================")
print("   CONSTRAINT TEST")
print("====================\n")

# Load input file
project_root = os.path.dirname(os.path.dirname(__file__))
input_path = os.path.join(project_root, "input", "input1.txt")

all_lines = read_all_lines(input_path)
sections = split_into_sections(all_lines)

# Parse prerequisite: events + slots
lec_by_id, course_list = parse_lectures(sections["Lectures:"])
tut_by_id, tut_list = parse_tutorials(sections["Tutorials:"])

events_by_id = {}
events_by_id.update(lec_by_id)
events_by_id.update(tut_by_id)

lec_slots_by_key, lec_slot_index = parse_lecture_slots(sections["Lecture slots:"])
tut_slots_by_key, tut_slot_index = parse_tutorial_slots(sections["Tutorial slots:"])

# PARSE EACH CONSTRAINT SECTION

# Not compatible
not_compat = parse_not_compatible(
    sections["Not compatible:"],
    events_by_id
)

print("\n--- NOT COMPATIBLE ---")
for nc in not_compat:
    print(nc)

# Unwanted
unwanted = parse_unwanted(
    sections["Unwanted:"],
    events_by_id,
    lec_slot_index,
    tut_slot_index
)

print("\n--- UNWANTED ---")
for uw in unwanted:
    print(uw)

# Preferences
prefs = parse_preferences(
    sections["Preferences:"],
    events_by_id,
    lec_slot_index,
    tut_slot_index
)

print("\n--- PREFERENCES ---")
for p in prefs:
    print(p)

# Pair
pairs = parse_pair(
    sections["Pair:"],
    events_by_id
)

print("\n--- PAIRS ---")
for pr in pairs:
    print(pr)

# Partial Assignments
partials = parse_partial_assignments(
    sections["Partial assignments:"],
    events_by_id,
    lec_slot_index,
    tut_slot_index
)

print("\n--- PARTIAL ASSIGNMENTS ---")
for pa in partials:
    print(pa)


# VALIDATION CHECKS

# Example Not Compatible (based on your input1.txt)
check(len(not_compat) > 0, "Not Compatible list is non-empty")

# Example unwanted check - updated for new constraint objects
for uw in unwanted:
    check(hasattr(uw, 'event_id') and hasattr(uw, 'slot_key'), "Unwanted entry has required attributes")

# Example preferences check - updated for new constraint objects
for p in prefs:
    check(hasattr(p, 'event_id') and hasattr(p, 'slot_key') and hasattr(p, 'value'), "Preference entry has required attributes")

# Example pair check - updated for new constraint objects
for pr in pairs:
    check(hasattr(pr, 'event_a_id') and hasattr(pr, 'event_b_id'), "Pair entry has required attributes")

# Example partial assignment check - updated for new constraint objects
for pa in partials:
    check(hasattr(pa, 'event_id') and hasattr(pa, 'slot_key'), "Partial assignment has required attributes")

print("\nALL CONSTRAINT TESTS PASSED SUCCESSFULLY!\n")