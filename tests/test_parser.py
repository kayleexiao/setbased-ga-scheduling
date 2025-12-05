"""
Test script for the parser.
Run from project root: python tests/test_parser.py input/input_2.txt
"""

import sys
import os

# add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from parser.parser import parse_input_file

def test_parser(input_file):
    """Test the parser with an input file."""
    
    print("=" * 80)
    print("TESTING PARSER")
    print("=" * 80)
    print(f"\nParsing file: {input_file}\n")
    
    try:
        # parse the input file
        problem = parse_input_file(
            input_file,
            pen_lecturemin=10,
            pen_tutorialmin=10,
            pen_notpaired=10,
            pen_section=10,
            w_minfilled=1,
            w_pref=1,
            w_pair=1,
            w_secdiff=1
        )
        
        print("\n" + "=" * 80)
        print("PARSING SUCCESSFUL!")
        print("=" * 80)
        
        # print summary
        print(f"\nProblem Name: {problem.name}")
        print(f"\nTotal Lectures: {len(problem.lec_by_id)}")
        print(f"Total Tutorials: {len(problem.tut_by_id)}")
        print(f"Total Events: {len(problem.events_by_id)}")
        print(f"\nLecture Slots: {len(problem.lec_slots_by_key)}")
        print(f"Tutorial Slots: {len(problem.tut_slots_by_key)}")
        
        print("\n" + "-" * 80)
        print("LECTURES:")
        print("-" * 80)
        for lec_id, lec in problem.lec_by_id.items():
            print(f"  {lec_id}")
            print(f"    - AL Required: {lec.al_required}")
            print(f"    - Evening: {lec.is_evening_event}")
            print(f"    - 500-level: {lec.is_500_course}")
        
        print("\n" + "-" * 80)
        print("TUTORIALS:")
        print("-" * 80)
        for tut_id, tut in problem.tut_by_id.items():
            print(f"  {tut_id}")
            print(f"    - Kind: {tut.kind}")
            print(f"    - AL Required: {tut.al_required}")
            print(f"    - Special: {tut.is_special_tut}")
        
        print("\n" + "-" * 80)
        print("LECTURE SLOTS:")
        print("-" * 80)
        for slot_key, slot in list(problem.lec_slots_by_key.items())[:10]:  # Show first 10
            print(f"  {slot.day} {slot.start_time}: max={slot.lecture_max}, min={slot.lecture_min}, AL={slot.al_lecture_max}")
            if slot.is_evening_slot:
                print(f"    [EVENING SLOT]")
            if slot.forbidden_for_lectures:
                print(f"    [FORBIDDEN - Department Meeting]")
        if len(problem.lec_slots_by_key) > 10:
            print(f"  ... and {len(problem.lec_slots_by_key) - 10} more lecture slots")
        
        print("\n" + "-" * 80)
        print("TUTORIAL SLOTS:")
        print("-" * 80)
        for slot_key, slot in list(problem.tut_slots_by_key.items())[:10]:  # Show first 10
            print(f"  {slot.day} {slot.start_time}: max={slot.tutorial_max}, min={slot.tutorial_min}, AL={slot.al_tutorial_max}")
            if slot.is_evening_slot:
                print(f"    [EVENING SLOT]")
            if slot.is_tth_18_19_tutorial:
                print(f"    [SPECIAL Tu/Th 18:00-19:00 SLOT]")
        if len(problem.tut_slots_by_key) > 10:
            print(f"  ... and {len(problem.tut_slots_by_key) - 10} more tutorial slots")
        
        print("\n" + "-" * 80)
        print("CONSTRAINTS:")
        print("-" * 80)
        print(f"Not Compatible: {len(problem.not_compatible)} constraints")
        for nc in problem.not_compatible[:5]:  # Show first 5
            print(f"  - {nc.event_a_id} NOT COMPATIBLE WITH {nc.event_b_id}")
        if len(problem.not_compatible) > 5:
            print(f"  ... and {len(problem.not_compatible) - 5} more")
        
        print(f"\nUnwanted: {len(problem.unwanted)} constraints")
        for uw in problem.unwanted[:5]:  # Show first 5
            print(f"  - {uw.event_id} UNWANTED IN {uw.slot_key}")
        if len(problem.unwanted) > 5:
            print(f"  ... and {len(problem.unwanted) - 5} more")
        
        print(f"\nPreferences: {len(problem.preferences)} preferences")
        for pref in problem.preferences[:5]:  # Show first 5
            print(f"  - {pref.event_id} IN {pref.slot_key}: penalty={pref.value}")
        if len(problem.preferences) > 5:
            print(f"  ... and {len(problem.preferences) - 5} more")
        
        print(f"\nPairs: {len(problem.pairs)} pairs")
        for pair in problem.pairs[:5]:  # Show first 5
            print(f"  - {pair.event_a_id} PAIRED WITH {pair.event_b_id}")
        if len(problem.pairs) > 5:
            print(f"  ... and {len(problem.pairs) - 5} more")
        
        print(f"\nPartial Assignments: {len(problem.partial_assignments)} assignments")
        for pa in problem.partial_assignments:
            print(f"  - {pa.event_id} ASSIGNED TO {pa.slot_key}")
        
        print("\n" + "-" * 80)
        print("PENALTIES & WEIGHTS:")
        print("-" * 80)
        print(f"Penalties:")
        print(f"  - Lecture Min: {problem.pen_lecturemin}")
        print(f"  - Tutorial Min: {problem.pen_tutorialmin}")
        print(f"  - Not Paired: {problem.pen_notpaired}")
        print(f"  - Section: {problem.pen_section}")
        print(f"\nWeights:")
        print(f"  - Min Filled: {problem.w_minfilled}")
        print(f"  - Preference: {problem.w_pref}")
        print(f"  - Pair: {problem.w_pair}")
        print(f"  - Section Diff: {problem.w_secdiff}")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE!")
        print("=" * 80)
        
        return problem
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("ERROR DURING PARSING!")
        print("=" * 80)
        print(f"\n{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tests/test_parser.py <input_file>")
        print("\nExample: python tests/test_parser.py input/input_2.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    test_parser(input_file)