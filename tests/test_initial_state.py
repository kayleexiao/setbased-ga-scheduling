# Test file for initial state generation

import sys
import os
import io
from contextlib import redirect_stdout

# add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.parser import parse_input_file
from model.initial_state import (
    generate_initial_state,
    print_population_summary,
    calculate_population_size
)


def print_detailed_population(population, problem_instance):
    """
    Print detailed view of all schedules in the population.
    Shows every assignment in every schedule (fact).
    
    Args:
        population: List of (schedule, eval, fitness, probability) tuples
        problem_instance: ProblemInstance
    """
    print("\n" + "="*70)
    print("DETAILED POPULATION VIEW - ALL FACTS (COMPLETE SCHEDULES)")
    print("="*70)
    
    for idx, (schedule, eval_score, fitness, probability) in enumerate(population, 1):
        print(f"\n{'─'*70}")
        print(f"FACT #{idx} - Complete Schedule")
        print(f"{'─'*70}")
        print(f"Eval: {eval_score}, Fitness: {fitness}")
        print(f"Probability: {probability}")
        print(f"Total Assignments: {schedule.count_assignments()}")
        
        # Separate lectures and tutorials
        lecture_assignments = []
        tutorial_assignments = []
        
        for event_id, slot_key in schedule.assignments.items():
            event = problem_instance.get_event(event_id)
            slot = problem_instance.get_slot(slot_key)
            
            if event and slot:
                assignment_info = {
                    'event_id': event_id,
                    'slot_key': slot_key,
                    'day': slot.day,
                    'time': slot.start_time,
                    'event': event,
                    'slot': slot
                }
                
                if event.is_lecture():
                    lecture_assignments.append(assignment_info)
                else:
                    tutorial_assignments.append(assignment_info)
        
        # Sort by day and time for better readability
        def sort_key(item):
            day_order = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4}
            return (day_order.get(item['day'], 5), item['time'])
        
        lecture_assignments.sort(key=sort_key)
        tutorial_assignments.sort(key=sort_key)
        
        # Print lectures
        print(f"\n  LECTURES ({len(lecture_assignments)}):")
        if lecture_assignments:
            for assign in lecture_assignments:
                event = assign['event']
                slot = assign['slot']
                al_marker = " [AL]" if event.al_required else ""
                evening_marker = " [EVENING]" if event.is_evening_event else ""
                print(f"    • {assign['event_id']:<30} > {slot.day}, {slot.start_time}{al_marker}{evening_marker}")
        else:
            print("    (none)")
        
        # Print tutorials
        print(f"\n  TUTORIALS ({len(tutorial_assignments)}):")
        if tutorial_assignments:
            for assign in tutorial_assignments:
                event = assign['event']
                slot = assign['slot']
                al_marker = " [AL]" if event.al_required else ""
                special_marker = " [SPECIAL]" if event.is_special_tut else ""
                print(f"    • {assign['event_id']:<30} > {slot.day}, {slot.start_time}{al_marker}{special_marker}")
        else:
            print("    (none)")
    
    print(f"\n{'='*70}")
    print(f"END OF POPULATION - Total Facts: {len(population)}")
    print(f"{'='*70}\n")


def print_compact_population(population, problem_instance):
    """
    Print a more compact view of the population showing just assignments.
    
    Args:
        population: List of (schedule, eval, fitness, probability) tuples
        problem_instance: ProblemInstance
    """
    print("\n" + "="*70)
    print("COMPACT POPULATION VIEW")
    print("="*70)
    
    for idx, (schedule, eval_score, fitness, probability) in enumerate(population, 1):
        print(f"\n[Fact #{idx}] Eval: {eval_score}, Fitness: {fitness}, Prob: {probability}, Assignments: {schedule.count_assignments()}")
        
        # Group by slot for compact display
        slot_to_events = {}
        for event_id, slot_key in schedule.assignments.items():
            if slot_key not in slot_to_events:
                slot_to_events[slot_key] = []
            slot_to_events[slot_key].append(event_id)
        
        # Print each slot with its assigned events
        for slot_key, event_ids in sorted(slot_to_events.items()):
            slot = problem_instance.get_slot(slot_key)
            if slot:
                print(f"  {slot.kind} {slot.day} {slot.start_time}:")
                for event_id in event_ids:
                    print(f"    - {event_id}")
    
    print(f"\n{'='*70}\n")


def test_initial_state_input2():
    """Test initial state generation with input2.txt"""
    print("\n" + "="*70)
    print("TEST: Initial State Generation with input2.txt")
    print("="*70)
    
    # Parse input file - use absolute path from project root
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input2.txt')
    
    problem = parse_input_file(
        input_path,
        pen_lecturemin=1,
        pen_tutorialmin=1,
        pen_notpaired=1,
        pen_section=1,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1
    )
    
    print(f"\nProblem loaded: {problem}")
    
    # Calculate recommended population size
    recommended_k = calculate_population_size(problem)
    print(f"\nRecommended population size k: {recommended_k}")
    
    # Generate initial population with recommended size
    population = generate_initial_state(problem, recommended_k)
    
    # Print summary
    print_population_summary(population, problem)
    
    # Print detailed view of all schedules
    print_detailed_population(population, problem)
    
    # Verify all schedules are complete
    total_events = len(problem.get_all_event_ids())
    all_complete = all(
        schedule.count_assignments() == total_events
        for schedule, _, _, _ in population
    )
    
    if all_complete:
        print("+ TEST PASSED: All schedules are complete")
    else:
        print("─ TEST FAILED: Some schedules are incomplete")
    
    return population, problem


def test_initial_state_custom_k():
    """Test initial state generation with custom k value"""
    print("\n" + "="*70)
    print("TEST: Initial State Generation with Custom k=5")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input2.txt')
    
    problem = parse_input_file(
        input_path,
        pen_lecturemin=1,
        pen_tutorialmin=1,
        pen_notpaired=1,
        pen_section=1,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1
    )
    
    # Generate with custom k
    k = 5
    population = generate_initial_state(problem, k, seed=42)
    
    print(f"\nGenerated population with k={k}")
    print(f"Actual population size: {len(population)}")
    
    if len(population) == k:
        print("+ TEST PASSED: Population size matches k")
    else:
        print("─ TEST FAILED: Population size does not match k")
    
    return population, problem


def test_type_safety():
    """Test that lectures only go to lecture slots and tutorials to tutorial slots"""
    print("\n" + "="*70)
    print("TEST: Type Safety (Lectures->Lecture Slots, Tutorials->Tutorial Slots)")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input2.txt')
    
    problem = parse_input_file(
        input_path,
        pen_lecturemin=1,
        pen_tutorialmin=1,
        pen_notpaired=1,
        pen_section=1,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1
    )
    
    # Generate population
    population = generate_initial_state(problem, k=10, seed=42)
    
    # Check type safety
    violations = []
    
    for idx, (schedule, _, _, _) in enumerate(population):
        for event_id, slot_key in schedule.assignments.items():
            event = problem.get_event(event_id)
            slot = problem.get_slot(slot_key)
            
            if event and slot:
                # Check if lecture is in lecture slot
                if event.is_lecture() and slot.kind != "LEC":
                    violations.append(f"Schedule {idx}: Lecture {event_id} in tutorial slot {slot_key}")
                
                # Check if tutorial is in tutorial slot
                if event.is_tutorial() and slot.kind != "TUT":
                    violations.append(f"Schedule {idx}: Tutorial {event_id} in lecture slot {slot_key}")
    
    if not violations:
        print("+ TEST PASSED: All events assigned to correct slot types")
    else:
        print("─ TEST FAILED: Type safety violations found:")
        for v in violations[:10]:  # Print first 10 violations
            print(f"  - {v}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more violations")
    
    return len(violations) == 0


def test_partial_assignments():
    """Test that partial assignments are respected"""
    print("\n" + "="*70)
    print("TEST: Partial Assignments Respected")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input2.txt')
    
    problem = parse_input_file(
        input_path,
        pen_lecturemin=1,
        pen_tutorialmin=1,
        pen_notpaired=1,
        pen_section=1,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1
    )
    
    print(f"\nNumber of partial assignments: {len(problem.partial_assignments)}")
    
    if len(problem.partial_assignments) == 0:
        print("Note: No partial assignments in this input file")
        return True
    
    # Generate population
    population = generate_initial_state(problem, k=10, seed=42)
    
    # Check that all schedules respect partial assignments
    violations = []
    
    for idx, (schedule, _, _, _) in enumerate(population):
        for pa in problem.partial_assignments:
            assigned_slot = schedule.get_assignment(pa.event_id)
            if assigned_slot != pa.slot_key:
                violations.append(
                    f"Schedule {idx}: Event {pa.event_id} assigned to {assigned_slot} "
                    f"instead of required {pa.slot_key}"
                )
    
    if not violations:
        print("+ TEST PASSED: All partial assignments respected")
    else:
        print("─ TEST FAILED: Partial assignment violations found:")
        for v in violations[:10]:
            print(f"  - {v}")
    
    return len(violations) == 0


def test_calculate_k():
    """Test the dynamic k calculation function"""
    print("\n" + "="*70)
    print("TEST: Dynamic k Calculation")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input2.txt')
    
    problem = parse_input_file(
        input_path,
        pen_lecturemin=1,
        pen_tutorialmin=1,
        pen_notpaired=1,
        pen_section=1,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1
    )
    
    # Test with different parameters
    k1 = calculate_population_size(problem, min_size=5, max_size=50, scale_factor=1.0)
    k2 = calculate_population_size(problem, min_size=10, max_size=100, scale_factor=2.0)
    k3 = calculate_population_size(problem, min_size=20, max_size=200, scale_factor=3.0)
    
    print(f"\nCalculated k values:")
    print(f"  - Conservative (scale=1.0, range=[5,50]): k={k1}")
    print(f"  - Moderate (scale=2.0, range=[10,100]): k={k2}")
    print(f"  - Aggressive (scale=3.0, range=[20,200]): k={k3}")
    
    # Verify k values are in valid ranges
    tests_passed = (
        5 <= k1 <= 50 and
        10 <= k2 <= 100 and
        20 <= k3 <= 200
    )
    
    if tests_passed:
        print("+ TEST PASSED: All k values within specified ranges")
    else:
        print("─ TEST FAILED: Some k values out of range")
    
    return tests_passed


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("RUNNING ALL INITIAL STATE TESTS")
    print("="*70)
    
    results = []
    
    try:
        test_initial_state_input2()
        results.append(("Initial State Generation", True))
    except Exception as e:
        print(f"─ TEST FAILED: Initial State Generation - {e}")
        import traceback
        traceback.print_exc()
        results.append(("Initial State Generation", False))
    
    try:
        test_initial_state_custom_k()
        results.append(("Custom k Value", True))
    except Exception as e:
        print(f"─ TEST FAILED: Custom k Value - {e}")
        results.append(("Custom k Value", False))
    
    try:
        passed = test_type_safety()
        results.append(("Type Safety", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Type Safety - {e}")
        results.append(("Type Safety", False))
    
    try:
        passed = test_partial_assignments()
        results.append(("Partial Assignments", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Partial Assignments - {e}")
        results.append(("Partial Assignments", False))
    
    try:
        passed = test_calculate_k()
        results.append(("Dynamic k Calculation", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Dynamic k Calculation - {e}")
        results.append(("Dynamic k Calculation", False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "+ PASSED" if passed else "─ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("="*70 + "\n")
    
    return passed_count == total_count


def run_detailed_view_only():
    """
    Run only the initial state generation and show detailed view.
    Useful for debugging and seeing all schedules.
    """
    print("\n" + "="*70)
    print("DETAILED VIEW MODE - Showing All Complete Schedules")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input2.txt')
    
    problem = parse_input_file(
        input_path,
        pen_lecturemin=1,
        pen_tutorialmin=1,
        pen_notpaired=1,
        pen_section=1,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1
    )
    
    print(f"\nProblem: {problem}")
    
    # Use smaller k for detailed view
    k = 5
    print(f"Generating {k} schedules for detailed inspection...")
    
    population = generate_initial_state(problem, k, seed=42)
    
    # Print both views
    print_population_summary(population, problem)
    print_detailed_population(population, problem)
    print_compact_population(population, problem)


if __name__ == "__main__":
    import sys
    
    # Capture all output
    output_buffer = io.StringIO()
    
    # Check if user wants detailed view only
    with redirect_stdout(output_buffer):
        if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
            run_detailed_view_only()
        else:
            success = run_all_tests()
    
    # Get captured output
    captured_output = output_buffer.getvalue()
    
    # Print to console
    print(captured_output)
    
    # Write to output file
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'test_initial_state_output.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(captured_output)
    
    print(f"\n+ Output written to: {output_file}")
    
    sys.exit(0 if success else 1)