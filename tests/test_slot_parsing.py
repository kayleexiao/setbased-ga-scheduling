import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.parser import read_all_lines, split_into_sections
from parser.slot import parse_lecture_slots, parse_tutorial_slots

def check(cond, msg):
    if cond:
        print(f"PASS: {msg}")
    else:
        print(f"FAIL: {msg}")
        raise AssertionError(msg)

print("\n==============================")
print(" FULL SLOT PARSING VALIDATION")
print("==============================\n")

# Load file
project_root = os.path.dirname(os.path.dirname(__file__))
input_path = os.path.join(project_root, "input", "input1.txt")

all_lines = read_all_lines(input_path)
sections = split_into_sections(all_lines)

lec_lines = sections["Lecture slots:"]
tut_lines = sections["Tutorial slots:"]

# Parse lecture slots
lec_by_key, lec_index = parse_lecture_slots(lec_lines)

print("\n--- LECTURE SLOTS BY KEY ---")
for key, slot in lec_by_key.items():
    print(f"{key} -> {slot}")

print("\n--- LECTURE SLOT INDEX (day,start) -> key ---")
for key, slot in lec_index.items():
    print(f"{key} -> {slot}")

# Parse tutorial slots
tut_by_key, tut_index = parse_tutorial_slots(tut_lines)

print("\n--- TUTORIAL SLOTS BY KEY ---")
for key, slot in tut_by_key.items():
    print(f"{key} -> {slot}")

print("\n--- TUTORIAL SLOT INDEX (day,start) -> key ---")
for key, slot in tut_index.items():
    print(f"{key} -> {slot}")

# Basic validation
check(("LEC", "MO", "8:00") in lec_by_key, "Lecture slot MO 8:00 exists")
check(("LEC", "MO", "9:00") in lec_by_key, "Lecture slot MO 9:00 exists")
check(("LEC", "TU", "9:30") in lec_by_key, "Lecture slot TU 9:30 exists")

check(("TUT", "MO", "8:00") in tut_by_key, "Tutorial slot MO 8:00 exists")
check(("TUT", "TU", "10:00") in tut_by_key, "Tutorial slot TU 10:00 exists")
check(("TUT", "FR", "10:00") in tut_by_key, "Tutorial slot FR 10:00 exists")

print("\nALL SLOT PARSING TESTS PASSED!\n")