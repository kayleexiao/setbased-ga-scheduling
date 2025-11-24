import os
from src.parser.parser import (
    read_all_lines,
    split_into_sections,
    parse_lectures,
    parse_tutorials,
    parse_lecture_slots,
    parse_tutorial_slots,
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

# Example unwanted check
for uw in unwanted:
    check("event_id" in uw and "slot_key" in uw, "Unwanted entry has required keys")

# Example preferences check
for p in prefs:
    check("event_id" in p and "slot" in p and "value" in p, "Preference entry has required keys")

# Example pair check
for pr in pairs:
    check("event_a_id" in pr and "event_b_id" in pr, "Pair entry has required keys")


# Example partial assignment check
for pa in partials:
    check("event_id" in pa and "slot" in pa, "Partial assignment has required keys")



print("\nALL CONSTRAINT TESTS PASSED SUCCESSFULLY!\n")