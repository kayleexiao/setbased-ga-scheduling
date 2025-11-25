import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.parser import read_all_lines, split_into_sections
from parser.event import parse_lectures, parse_tutorials

def check(condition, message):
    if condition:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")
        raise AssertionError(message)

print("\n==============================")
print(" FULL EVENT PARSING VALIDATION")
print("==============================\n")

# Load input file
project_root = os.path.dirname(os.path.dirname(__file__))
input_path = os.path.join(project_root, "input", "input1.txt")

all_lines = read_all_lines(input_path)
print(f"Total lines read: {len(all_lines)}")

# Split into sections
sections = split_into_sections(all_lines)
print(f"Total sections found: {len(sections)}")
print("Sections:", list(sections.keys()), "\n")

# Required sections
required = ["Lectures:", "Tutorials:"]
for sec in required:
    check(sec in sections, f"Section exists: {sec}")


# Parse ALL lectures
lecture_lines = sections["Lectures:"]
lec_by_id, course_list = parse_lectures(lecture_lines)

print("\n--- LECTURE IDS ---")
for eid in lec_by_id:
    print(eid)

print("\n--- LECTURE OBJECTS (lec_by_id) ---")
for k, v in lec_by_id.items():
    print(f"{k} -> {v}")

print("\n--- LECTURE GROUPS (course_list) ---")
for course, ids in course_list.items():
    print(f"{course}: {ids}")

expected_lectures = [
    "CPSC 231 LEC 01",
    "CPSC 231 LEC 02",
    "DATA 201 LEC 01",
    "SENG 300 LEC 01",
]

for eid in expected_lectures:
    check(eid in lec_by_id, f"Lecture parsed: {eid}")

# Parse ALL tutorials
tutorial_lines = sections["Tutorials:"]
tut_by_id, tut_list = parse_tutorials(tutorial_lines)

print("\n--- TUTORIAL IDS ---")
for eid in tut_by_id:
    print(eid)

print("\n--- TUTORIAL OBJECTS (tut_by_id) ---")
for k, v in tut_by_id.items():
    print(f"{k} -> {v}")

print("\n--- TUTORIAL GROUPS (tut_list) ---")
for course, ids in tut_list.items():
    print(f"{course}: {ids}")

expected_tutorials = [
    "CPSC 231 LEC 01 TUT 01",
    "CPSC 231 LEC 02 TUT 02",
    "DATA 201 LEC 01 LAB 01",
    "SENG 300 TUT 01",
]

for eid in expected_tutorials:
    check(eid in tut_by_id, f"Tutorial parsed: {eid}")

# Combine into events_by_id
events_by_id = {}
events_by_id.update(lec_by_id)
events_by_id.update(tut_by_id)

print("\n--- ALL EVENTS (events_by_id) ---")
for k in events_by_id:
    print(k)

# Spot check event existence
check("CPSC 231 LEC 01" in events_by_id, "Event exists: CPSC 231 LEC 01")
check("CPSC 231 LEC 01 TUT 01" in events_by_id, "Event exists: CPSC 231 LEC 01 TUT 01")

print("\nALL EVENT PARSING TESTS PASSED SUCCESSFULLY!\n")