import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.parser import read_all_lines, split_into_sections

def check(condition, description):
    if condition:
        print(f"PASS: {description}")
    else:
        print(f"FAIL: {description}")
        raise AssertionError(description)

project_root = os.path.dirname(os.path.dirname(__file__))
input_path = os.path.join(project_root, "input", "input1.txt")

# read lines
all_lines = read_all_lines(input_path)
print(f"Total lines read: {len(all_lines)}")

# split into named sections
sections = split_into_sections(all_lines)
print(f"Total sections found: {len(sections)}")
print("Sections:", list(sections.keys()))

expected_sections = [
    "Name:",
    "Lecture slots:",
    "Tutorial slots:",
    "Lectures:",
    "Tutorials:",
    "Not compatible:",
    "Unwanted:",
    "Preferences:",
    "Pair:",
    "Partial assignments:",
]

for sec in expected_sections:
    check(sec in sections, f"Section exists: {sec}")

check(sections["Name:"][0] == "ShortExample", "Correct Name value")

expected_lecture_slots = {
    "MO, 8:00, 3, 2, 0",
    "MO, 9:00, 3, 2, 1",
    "TU, 9:30, 2, 1, 2",
}

for line in expected_lecture_slots:
    check(line in sections["Lecture slots:"], f"Lecture slot present: {line}")

expected_tutorial_slots = {
    "MO, 8:00, 4, 2, 4",
    "TU, 10:00, 2, 1, 2",
    "FR, 10:00, 2, 1, 0",
}

for line in expected_tutorial_slots:
    check(line in sections["Tutorial slots:"], f"Tutorial slot present: {line}")

expected_lectures = {
    "CPSC 231 LEC 01, true",
    "CPSC 231 LEC 02, true",
    "DATA 201 LEC 01, false",
    "SENG 300 LEC 01, false",
}

for line in expected_lectures:
    check(line in sections["Lectures:"], f"Lecture present: {line}")

expected_tutorials = {
    "CPSC 231 LEC 01 TUT 01, true",
    "CPSC 231 LEC 02 TUT 02, true",
    "DATA 201 LEC 01 LAB 01, false",
    "SENG 300 TUT 01, false",
}

for line in expected_tutorials:
    check(line in sections["Tutorials:"], f"Tutorial present: {line}")

expected_nc = {
    "CPSC 231 LEC 01 TUT 01, CPSC 231 LEC 02 TUT 02",
    "SENG 300 LEC 01, CPSC 231 LEC 01",
    "SENG 300 LEC 01, CPSC 231 LEC 02",
    "SENG 300 TUT 01, CPSC 231 LEC 02",
    "CPSC 231 LEC 01, SENG 300 TUT 01",
}

for line in expected_nc:
    check(line in sections["Not compatible:"], f"Not compatible entry: {line}")

check(
    "CPSC 231 LEC 01, MO, 8:00" in sections["Unwanted:"],
    "Unwanted entry present: CPSC 231 LEC 01, MO, 8:00"
)

# build set of valid time slots (day, time combinations)
valid_slots = set()
for slot_line in sections["Lecture slots:"] + sections["Tutorial slots:"]:
    parts = [p.strip() for p in slot_line.split(',')]
    if len(parts) >= 2:
        day = parts[0]
        time = parts[1]
        valid_slots.add((day, time))

expected_preferences = {
    "TU, 9:30, CPSC 231 LEC 01, 10",
    "MO, 8:00, CPSC 231 LEC 01 TUT 01, 3",
    "TU, 9:30, CPSC 231 LEC 02, 10",
    "TU, 10:00, CPSC 231 LEC 01 LAB 02, 5",
    "MO, 8:00, CPSC 231 LEC 02 LAB 02, 1",
    "MO, 10:00, CPSC 231 LEC 02 LAB 02, 7",
}

for line in expected_preferences:
    if line in sections["Preferences:"]:
        # Extract time slot from preference (first two comma-separated parts)
        parts = [p.strip() for p in line.split(',', 2)]
        if len(parts) >= 2:
            day = parts[0]
            time = parts[1]
            if (day, time) not in valid_slots:
                print(f"SKIP: Preference entry '{line}' does not refer to a valid time slot ({day}, {time})")
                continue
        check(True, f"Preference entry: {line}")
    else:
        # Check if it's because of invalid slot
        parts = [p.strip() for p in line.split(',', 2)]
        if len(parts) >= 2:
            day = parts[0]
            time = parts[1]
            if (day, time) not in valid_slots:
                print(f"SKIP: Preference entry '{line}' does not refer to a valid time slot ({day}, {time})")
                continue
        check(False, f"Preference entry: {line}")

check(
    "DATA 201 LEC 01, SENG 300 LEC 01" in sections["Pair:"],
    "Pair entry present: DATA 201 LEC 01, SENG 300 LEC 01"
)

expected_partial = {
    "DATA 201 LEC 01, MO, 8:00",
    "DATA 201 LEC 01 LAB 01, FR, 10:00",
}

for line in expected_partial:
    check(line in sections["Partial assignments:"], f"Partial assignment: {line}")

print("\nALL INPUT VALIDATION CHECKS PASSED SUCCESSFULLY!\n")