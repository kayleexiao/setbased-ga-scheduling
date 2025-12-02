# Test file for initial state generation with eval/fitness integration

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
from eval.eval import eval
from eval.hard_constraints import Valid
from eval.selection import fitness


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
    
    for idx, (schedule, eval_score, fitness_score, probability) in enumerate(population, 1):
        # Compute hard constraint penalty for display
        hard_penalty = Valid(schedule, problem_instance)
        
        print(f"\n{'─'*70}")
        print(f"FACT #{idx} - Complete Schedule")
        print(f"{'─'*70}")
        print(f"Hard Constraint Penalty (Valid): {hard_penalty}")
        print(f"Soft Constraint Penalty (Eval): {eval_score}")
        print(f"Fitness Score: {fitness_score:.6f}")
        print(f"Probability: {probability:.6f}")
        print(f"Total Assignments: {schedule.count_assignments()}")
        
        # Status indicator
        if hard_penalty == 0:
            print("Status: + VALID (satisfies all hard constraints)")
        else:
            print(f"Status: ─ INVALID ({hard_penalty} hard constraint violations)")
        
        # Separate lectures and tutorials
        lecture_assignments = []
        tutorial_assignments = []
        
        for event, slot in schedule.assignments.items():
            assignment_info = {
                'event_id': event.id,
                'event': event,
                'slot': slot,
                'day': slot.day,
                'time': slot.start_time
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
                special_500 = " [500-LEVEL]" if event.is_500_course else ""
                print(f"    • {assign['event_id']:<30} → {slot.day}, {slot.start_time}{al_marker}{evening_marker}{special_500}")
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
                print(f"    • {assign['event_id']:<30} → {slot.day}, {slot.start_time}{al_marker}{special_marker}")
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
    
    for idx, (schedule, eval_score, fitness_score, probability) in enumerate(population, 1):
        hard_penalty = Valid(schedule, problem_instance)
        status = "+" if hard_penalty == 0 else "─"
        print(f"\n[Fact #{idx}] {status} Valid:{hard_penalty} Eval:{eval_score} Fit:{fitness_score:.4f} Prob:{probability:.4f} Assignments:{schedule.count_assignments()}")
        
        # Group by slot for compact display
        slot_to_events = {}
        for event, slot in schedule.assignments.items():
            slot_key = (slot.kind, slot.day, slot.start_time)
            if slot_key not in slot_to_events:
                slot_to_events[slot_key] = []
            slot_to_events[slot_key].append(event.id)
        
        # Print each slot with its assigned events
        for slot_key, event_ids in sorted(slot_to_events.items()):
            kind, day, time = slot_key
            print(f"  {kind} {day} {time}:")
            for event_id in event_ids:
                print(f"    - {event_id}")
    
    print(f"\n{'='*70}\n")


def test_initial_state_input2():
    """Test initial state generation with input1.txt"""
    print("\n" + "="*70)
    print("TEST: Initial State Generation with input1.txt")
    print("="*70)
    
    # Parse input file - use absolute path from project root
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    # Use w_hard=10 and w_soft=1 as per your proposal
    population = generate_initial_state(
        problem_instance=problem,
        k=recommended_k,
        w_hard=10,
        w_soft=1,
        seed=42  # for reproducibility
    )
    
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
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    population = generate_initial_state(
        problem_instance=problem,
        k=k,
        w_hard=10,
        w_soft=1,
        seed=42
    )
    
    print(f"\nGenerated population with k={k}")
    print(f"Actual population size: {len(population)}")
    
    # Verify tuple structure
    print("\nVerifying tuple structure for each individual:")
    for idx, individual in enumerate(population, 1):
        schedule, eval_val, fit_val, prob_val = individual
        print(f"  Fact #{idx}: eval={eval_val}, fitness={fit_val:.6f}, prob={prob_val:.6f}")
    
    if len(population) == k:
        print("\n+ TEST PASSED: Population size matches k")
    else:
        print(f"\n─ TEST FAILED: Population size {len(population)} does not match k={k}")
    
    return population, problem


def test_type_safety():
    """Test that lectures only go to lecture slots and tutorials to tutorial slots"""
    print("\n" + "="*70)
    print("TEST: Type Safety (Lectures→Lecture Slots, Tutorials→Tutorial Slots)")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    population = generate_initial_state(
        problem_instance=problem,
        k=10,
        w_hard=10,
        w_soft=1,
        seed=42
    )
    
    # Check type safety
    violations = []
    
    for idx, (schedule, _, _, _) in enumerate(population):
        for event, slot in schedule.assignments.items():
            # Check if lecture is in lecture slot
            if event.is_lecture() and slot.kind != "LEC":
                violations.append(f"Schedule {idx}: Lecture {event.id} in tutorial slot {slot}")
            
            # Check if tutorial is in tutorial slot
            if event.is_tutorial() and slot.kind != "TUT":
                violations.append(f"Schedule {idx}: Tutorial {event.id} in lecture slot {slot}")
    
    if not violations:
        print("+ TEST PASSED: All events assigned to correct slot types")
    else:
        print("─ TEST FAILED: Type safety violations found:")
        for v in violations[:10]:  # Print first 10 violations
            print(f"  - {v}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more violations")
    
    return len(violations) == 0


def test_eval_fitness_computed():
    """Test that eval and fitness values are properly computed (not placeholders)"""
    print("\n" + "="*70)
    print("TEST: Eval and Fitness Values Properly Computed")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    population = generate_initial_state(
        problem_instance=problem,
        k=10,
        w_hard=10,
        w_soft=1,
        seed=42
    )
    
    print(f"\nGenerated {len(population)} schedules")
    print("\nVerifying eval and fitness computation:")
    
    all_valid = True
    for idx, (schedule, eval_val, fit_val, prob_val) in enumerate(population, 1):
        # Manually recompute to verify
        expected_eval = eval(schedule, problem)
        expected_valid = Valid(schedule, problem)
        
        # Compute expected fitness
        expected_fitness = 1 / (1 + 10 * expected_valid + 1 * expected_eval)
        
        # Check if values match
        eval_matches = (eval_val == expected_eval)
        fitness_matches = abs(fit_val - expected_fitness) < 0.0001  # floating point tolerance
        
        status = "+" if (eval_matches and fitness_matches) else "─"
        print(f"  {status} Fact #{idx}:")
        print(f"      Stored: eval={eval_val}, fitness={fit_val:.6f}")
        print(f"      Expected: eval={expected_eval}, fitness={expected_fitness:.6f}")
        
        if not (eval_matches and fitness_matches):
            all_valid = False
            print(f"      MISMATCH DETECTED!")
    
    if all_valid:
        print("\n+ TEST PASSED: All eval and fitness values correctly computed")
    else:
        print("\n─ TEST FAILED: Some eval/fitness values incorrect")
    
    return all_valid


def test_fitness_formula():
    """Test that fitness formula matches the proposal specification"""
    print("\n" + "="*70)
    print("TEST: Fitness Formula = 1/(1 + w_hard*Valid + w_soft*Eval)")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    
    # Test with different weight configurations
    weight_configs = [
        (10, 1),   # Default from proposal
        (10, 0.7), # Alternative from proposal
        (1, 1),    # Equal weights
        (100, 1),  # Heavy hard constraint emphasis
    ]
    
    all_passed = True
    
    for w_hard, w_soft in weight_configs:
        print(f"\nTesting with w_hard={w_hard}, w_soft={w_soft}:")
        
        population = generate_initial_state(
            problem_instance=problem,
            k=5,
            w_hard=w_hard,
            w_soft=w_soft,
            seed=42
        )
        
        for idx, (schedule, eval_val, fit_val, _) in enumerate(population, 1):
            valid_val = Valid(schedule, problem)
            expected_fitness = 1 / (1 + w_hard * valid_val + w_soft * eval_val)
            
            matches = abs(fit_val - expected_fitness) < 0.0001
            status = "+" if matches else "─"
            
            print(f"  {status} Fact #{idx}: valid={valid_val}, eval={eval_val}, fitness={fit_val:.6f} (expected {expected_fitness:.6f})")
            
            if not matches:
                all_passed = False
    
    if all_passed:
        print("\n+ TEST PASSED: Fitness formula correctly implemented")
    else:
        print("\n─ TEST FAILED: Fitness formula mismatch")
    
    return all_passed


def test_partial_assignments():
    """Test that partial assignments are respected"""
    print("\n" + "="*70)
    print("TEST: Partial Assignments Respected")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
        print("+ TEST PASSED: (No partial assignments to test)")
        return True
    
    # Print partial assignments
    for pa in problem.partial_assignments:
        print(f"  - {pa.event_id} must be in slot {pa.slot_key}")
    
    # Generate population
    population = generate_initial_state(
        problem_instance=problem,
        k=10,
        w_hard=10,
        w_soft=1,
        seed=42
    )
    
    # Check that all schedules respect partial assignments
    violations = []
    
    for idx, (schedule, _, _, _) in enumerate(population):
        for pa in problem.partial_assignments:
            event = problem.get_event(pa.event_id)
            if event is None:
                continue
                
            assigned_slot = schedule.get_assignment(event)
            expected_slot = problem.get_slot(pa.slot_key)
            
            if assigned_slot != expected_slot:
                violations.append(
                    f"Schedule {idx}: Event {pa.event_id} assigned to {assigned_slot} "
                    f"instead of required {expected_slot}"
                )
    
    if not violations:
        print("\n+ TEST PASSED: All partial assignments respected")
    else:
        print("\n─ TEST FAILED: Partial assignment violations found:")
        for v in violations[:10]:
            print(f"  - {v}")
    
    return len(violations) == 0


def test_calculate_k():
    """Test the dynamic k calculation function"""
    print("\n" + "="*70)
    print("TEST: Dynamic k Calculation")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
        print("\n+ TEST PASSED: All k values within specified ranges")
    else:
        print("\n─ TEST FAILED: Some k values out of range")
    
    return tests_passed


def test_probability_initialization():
    """Test that probability values are initialized to 0 (not computed yet)"""
    print("\n" + "="*70)
    print("TEST: Probability Initialization (should be 0)")
    print("="*70)
    
    # Parse input file
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    
    population = generate_initial_state(
        problem_instance=problem,
        k=10,
        w_hard=10,
        w_soft=1,
        seed=42
    )
    
    all_zero = all(prob == 0 for _, _, _, prob in population)
    
    if all_zero:
        print("+ TEST PASSED: All probability values initialized to 0")
    else:
        print("─ TEST FAILED: Some probability values are not 0")
        for idx, (_, _, _, prob) in enumerate(population, 1):
            if prob != 0:
                print(f"  Fact #{idx} has probability {prob}")
    
    return all_zero


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("RUNNING ALL INITIAL STATE TESTS")
    print("="*70)
    
    results = []
    
    # Test 1: Basic initial state generation
    try:
        test_initial_state_input2()
        results.append(("Initial State Generation", True))
    except Exception as e:
        print(f"─ TEST FAILED: Initial State Generation - {e}")
        import traceback
        traceback.print_exc()
        results.append(("Initial State Generation", False))
    
    # Test 2: Custom k value
    try:
        test_initial_state_custom_k()
        results.append(("Custom k Value", True))
    except Exception as e:
        print(f"─ TEST FAILED: Custom k Value - {e}")
        results.append(("Custom k Value", False))
    
    # Test 3: Type safety
    try:
        passed = test_type_safety()
        results.append(("Type Safety", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Type Safety - {e}")
        results.append(("Type Safety", False))
    
    # Test 4: Eval/Fitness computation
    try:
        passed = test_eval_fitness_computed()
        results.append(("Eval/Fitness Computation", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Eval/Fitness Computation - {e}")
        import traceback
        traceback.print_exc()
        results.append(("Eval/Fitness Computation", False))
    
    # Test 5: Fitness formula
    try:
        passed = test_fitness_formula()
        results.append(("Fitness Formula", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Fitness Formula - {e}")
        results.append(("Fitness Formula", False))
    
    # Test 6: Partial assignments
    try:
        passed = test_partial_assignments()
        results.append(("Partial Assignments", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Partial Assignments - {e}")
        results.append(("Partial Assignments", False))
    
    # Test 7: Dynamic k calculation
    try:
        passed = test_calculate_k()
        results.append(("Dynamic k Calculation", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Dynamic k Calculation - {e}")
        results.append(("Dynamic k Calculation", False))
    
    # Test 8: Probability initialization
    try:
        passed = test_probability_initialization()
        results.append(("Probability Initialization", passed))
    except Exception as e:
        print(f"─ TEST FAILED: Probability Initialization - {e}")
        results.append(("Probability Initialization", False))
    
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
    input_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'input1.txt')
    
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
    
    population = generate_initial_state(
        problem_instance=problem,
        k=k,
        w_hard=10,
        w_soft=1,
        seed=42
    )
    
    # Print both views
    print_population_summary(population, problem)
    print_detailed_population(population, problem)
    print_compact_population(population, problem)


if __name__ == "__main__":
    import sys
    
    # Capture all output
    output_buffer = io.StringIO()
    
    with redirect_stdout(output_buffer):
        # Check if user wants detailed view only
        if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
            run_detailed_view_only()
            success = True
        else:
            # Run all tests
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