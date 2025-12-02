# Initial state (Facts) generation

import random
import sys
import os

# add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.schedule import Schedule

def generate_initial_state(problem_instance, k, seed=None):
    """
    Generate set of facts/initial state s_0 for GA search containing k complete schedules.
    
    A complete schedule assigns ALL lectures and tutorials to time slots.
    
    ASSIGNMENT RULES:
    - Lectures > randomly assigned to lecture slots
    - Tutorials > randomly assigned to tutorial slots
    - Partial assignments are respected
    - No other constraints considered (completely random)

    Args:
        problem_instance: ProblemInstance with all parsed data
        k: Population size (number of complete schedules to generate)
        seed: Random seed for reproducibility (optional, probably use for testing/debugging)
    
    Returns:
        List of tuples: [(schedule_1, eval_1, fitness_1, probability_1), ..., (schedule_k, eval_k, fitness_k, probability_k)]
        where each schedule is a complete random assignment, eval is placeholder 0, fitness is placeholder 0, and probability is placeholder 0.5
    """
    if seed is not None:
        random.seed(seed)
    
    population = []
    
    # generate k complete schedules
    for i in range(k):
        schedule = generate_single_complete_schedule(problem_instance)
        # store as tuple (schedule, eval, fitness, probability)
        # eval initialized to 0, will be UPDATED by evaluation function
        # fitness initialized to 0, will be UPDATED by fitness function
        # probability initialized to 0.5 (placeholder), will be UPDATED by probability function
        population.append((schedule, 0, 0, 0.5))
    
    return population

# function to generate a single complete random schedule, assigning all events
# returns Schedule object
# see docstring in generate_initial_state for assignment rules
def generate_single_complete_schedule(problem_instance):
    schedule = Schedule()
    
    # step 1: handle partial assignments first (these are fixed)
    # ///// LATER: EDIT TO TERMINATE IF PARTIAL ASSIGNMENTS INVALID /////
        # - lec with a slot that is not a lec slot or tut with a slot that is not a tut slot
    for pa in problem_instance.partial_assignments:
        schedule.assign(pa.event_id, pa.slot_key)
    
    # step 2: get all available lecture and tutorial slots
    lecture_slot_keys = problem_instance.get_all_lecture_slot_keys() # contains only lec slots
    tutorial_slot_keys = problem_instance.get_all_tutorial_slot_keys() # contains only tut slots
    
    if not lecture_slot_keys:
        raise ValueError("No lecture slots available in problem instance!")
    if not tutorial_slot_keys:
        raise ValueError("No tutorial slots available in problem instance!")
    
    # step 3: randomly assign all LECTURES to random LECTURE SLOTS
    for lecture_id in problem_instance.get_all_lecture_ids():
        if schedule.is_assigned(lecture_id):
            continue  # already has partial assignment
        
        # pick a completely random lecture slot
        random_slot = random.choice(lecture_slot_keys)
        schedule.assign(lecture_id, random_slot)
    
    # step 4: randomly assign all TUTORIALS to random TUTORIAL SLOTS
    for tutorial_id in problem_instance.get_all_tutorial_ids():
        if schedule.is_assigned(tutorial_id):
            continue  # already has partial assignment
        
        # pick a completely random tutorial slot
        random_slot = random.choice(tutorial_slot_keys)
        schedule.assign(tutorial_id, random_slot)
    
    return schedule

# function to dynamically calculate population size k based on problem complexity
# returns population size k (int)
def calculate_population_size(problem_instance, min_size=10, max_size=100, scale_factor=2.0):
    num_events = len(problem_instance.get_all_event_ids())
    num_slots = len(problem_instance.get_all_lecture_slot_keys()) + \
                len(problem_instance.get_all_tutorial_slot_keys())
    
    # calculate based on problem complexity
    # use geometric mean of events and slots for balanced scaling
    complexity = (num_events * num_slots) ** 0.5
    
    # scale by factor and round to nearest integer
    k = int(complexity * scale_factor)
    
    # clamp to min/max bounds
    k = max(min_size, min(k, max_size))
    
    return k


def print_population_summary(population, problem_instance):
    """
    Print summary statistics about the initial population.
    
    Args:
        population: List of (schedule, eval, fitness, probability) tuples
        problem_instance: ProblemInstance
    """
    print(f"\n{'='*60}")
    print(f"INITIAL POPULATION SUMMARY")
    print(f"{'='*60}")
    print(f"Population size: {len(population)}")
    
    total_events = len(problem_instance.get_all_event_ids())
    print(f"Total events to schedule: {total_events}")
    print(f"  - Lectures: {len(problem_instance.get_all_lecture_ids())}")
    print(f"  - Tutorials: {len(problem_instance.get_all_tutorial_ids())}")
    
    print(f"\nAvailable slots:")
    print(f"  - Lecture slots: {len(problem_instance.get_all_lecture_slot_keys())}")
    print(f"  - Tutorial slots: {len(problem_instance.get_all_tutorial_slot_keys())}")
    
    print(f"\nConstraints:")
    print(f"  - Partial assignments: {len(problem_instance.partial_assignments)}")
    print(f"  - Not compatible pairs: {len(problem_instance.not_compatible)}")
    print(f"  - Unwanted assignments: {len(problem_instance.unwanted)}")
    print(f"  - Preferences: {len(problem_instance.preferences)}")
    print(f"  - Pair constraints: {len(problem_instance.pairs)}")
    
    # check completeness of schedules
    print(f"\nSchedule completeness check:")
    for i, (schedule, _, _, _) in enumerate(population):
        assigned = schedule.count_assignments()
        complete = "+" if assigned == total_events else "─"
        print(f"  Schedule {i+1}: {assigned}/{total_events} events assigned {complete}")
    
    print(f"{'='*60}\n")


