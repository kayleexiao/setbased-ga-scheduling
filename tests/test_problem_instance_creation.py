import os
from src.parser.parser import parse_problem_instance

def check(cond, msg):
    if cond:
        print(f"PASS: {msg}")
    else:
        print(f"FAIL: {msg}")
        raise AssertionError(msg)


print("\n====================================================")
print("        FULL PROBLEM INSTANCE PARSING TEST")
print("====================================================\n")

# Load file
project_root = os.path.dirname(os.path.dirname(__file__))
input_path = os.path.join(project_root, "input", "input1.txt")

print(f"Loading problem instance from: {input_path}\n")

inst = parse_problem_instance(input_path)

# PRINT EVERYTHING

print("=======================================")
print("               META")
print("=======================================\n")
print("Problem Name:", inst.name)

print("\n=======================================")
print("               EVENTS")
print("=======================================\n")

print("lec_by_id:")
for eid in inst.lec_by_id:
    print("  ", eid)

print("\nLecture Objects:")
for eid, obj in inst.lec_by_id.items():
    print("  ", eid, "->", obj)

print("\ntut_by_id")
for eid in inst.tut_by_id:
    print("  ", eid)

print("\nTutorial Objects:")
for eid, obj in inst.tut_by_id.items():
    print("  ", eid, "->", obj)

print("\nevents_by_id:")
for eid in inst.events_by_id:
    print("  ", eid)

print("\ncourse_list:")
for key, items in inst.course_list.items():
    print("  ", key, "->", items)

print("\ntut_list:")
for key, items in inst.tut_list.items():
    print("  ", key, "->", items)


print("\n=======================================")
print("               SLOTS")
print("=======================================\n")

print("lec_slots_by_key:")
for key, slot in inst.lec_slots_by_key.items():
    print("  ", key, "->", slot)

print("\nlec_slot_index:")
for key, skey in inst.lec_slot_index.items():
    print("  ", key, "->", skey)

print("\ntut_slots_by_key:")
for key, slot in inst.tut_slots_by_key.items():
    print("  ", key, "->", slot)

print("\ntut_slot_index:")
for key, skey in inst.tut_slot_index.items():
    print("  ", key, "->", skey)


print("\n=======================================")
print("               CONSTRAINTS")
print("=======================================\n")

print("not_compatible:")
for c in inst.not_compatible:
    print("  ", c)

print("\nunwanted:")
for u in inst.unwanted:
    print("  ", u)

print("\npreferences:")
for p in inst.preferences:
    print("  ", p)

print("\npairs:")
for pr in inst.pairs:
    print("  ", pr)

print("\npartial_assignments:")
for pa in inst.partial_assignments:
    print("  ", pa)

print("\n=======================================")
print("      REQUIREMENT CHECKS")
print("=======================================\n")

required_fields = [
    "name",
    "lec_by_id", "events_by_id", "course_list", "tut_list",
    "lec_slots_by_key", "tut_slots_by_key", "lec_slot_index", "tut_slot_index",
    "not_compatible", "unwanted", "preferences", "pairs", "partial_assignments"
]

for field in required_fields:
    check(hasattr(inst, field), f"ProblemInstance has required field: {field}")

print("\n=======================================")
print("      TYPE + CONTENT CHECKS")
print("=======================================\n")

# Meta
check(isinstance(inst.name, str), "name is string")

# Events
check(isinstance(inst.lec_by_id, dict), "lec_by_id is dict")
check(isinstance(inst.events_by_id, dict), "events_by_id is dict")
check(isinstance(inst.course_list, dict), "course_list is dict")
check(isinstance(inst.tut_list, dict), "tut_list is dict")

check(len(inst.lec_by_id) > 0, "lec_by_id contains entries")
check(len(inst.tut_by_id) > 0, "tut_by_id contains entries")
check(len(inst.events_by_id) == len(inst.lec_by_id) + len(inst.tut_by_id),
      "events_by_id merges lectures+tutorials")

# Slots
check(isinstance(inst.lec_slots_by_key, dict), "lec_slots_by_key is dict")
check(isinstance(inst.tut_slots_by_key, dict), "tut_slots_by_key is dict")
check(isinstance(inst.lec_slot_index, dict), "lec_slot_index is dict")
check(isinstance(inst.tut_slot_index, dict), "tut_slot_index is dict")

check(len(inst.lec_slots_by_key) > 0, "lecture slots non-empty")
check(len(inst.tut_slots_by_key) > 0, "tutorial slots non-empty")
check(len(inst.lec_slot_index) == len(inst.lec_slots_by_key),
      "lec_slot_index length matches number of lecture slots")
check(len(inst.tut_slot_index) == len(inst.tut_slots_by_key),
      "tut_slot_index length matches number of tutorial slots")

# Constraints
check(isinstance(inst.not_compatible, list), "not_compatible is list")
check(isinstance(inst.unwanted, list), "unwanted is list")
check(isinstance(inst.preferences, list), "preferences is list")
check(isinstance(inst.pairs, list), "pairs is list")
check(isinstance(inst.partial_assignments, list), "partial_assignments is list")

check(len(inst.not_compatible) > 0, "not_compatible non-empty")
check(len(inst.unwanted) > 0, "unwanted non-empty")
check(len(inst.preferences) > 0, "preferences non-empty")
check(len(inst.pairs) > 0, "pairs non-empty")
check(len(inst.partial_assignments) > 0, "partial_assignments non-empty")


print("\n==================================================")
print("  ALL TESTS PASSED - ProblemInstance is valid!")
print("==================================================\n")
