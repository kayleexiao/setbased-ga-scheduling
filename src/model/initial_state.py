# Initial state (Facts) generation

import random
import sys
import os

# add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.schedule import Schedule
from eval.eval import eval
from eval.hard_constraints import Valid
from eval.selection import fitness

def generate_initial_state(problem_instance, k, w_hard=10, w_soft=1, seed=None):
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
        w_hard: Weight for hard constraint violations (default: 10)
        w_soft: Weight for soft constraint violations (default: 1)
        seed: Random seed for reproducibility (optional, probably use for testing/debugging)
            - used seed = 42 for initial testing, gives 1 valid schedule for input1
    
    Returns:
        List of tuples: [(schedule_1, eval_1, fitness_1, probability_1), ..., (schedule_k, eval_k, fitness_k, probability_k)]
        where:
        - schedule: Schedule object with complete random assignment
        - eval: soft constraint penalty computed by eval()
        - fitness: fitness score computed by fitness()
        - probability: placeholder 0 (will be updated by probability() function later during roulette wheel selection in search)
    """
    if seed is not None:
        random.seed(seed)
    
    population = []
    
    # generate k complete schedules
    for i in range(k):
        schedule = generate_single_complete_schedule(problem_instance)
        # store as tuple (schedule, eval, fitness, probability)
        
        # compute eval score (soft constraints)
        eval_score = eval(schedule, problem_instance)
        
        # create tuple with placeholder fitness and probability
        # fitness function expects tuple format: (schedule, eval, fitness, probability)
        individual = (schedule, eval_score, 0, 0)
        
        # compute fitness using the fitness function
        # fitness returns updated tuple with new fitness score
        individual_with_fitness = fitness(individual, problem_instance, w_hard, w_soft)
        
        # extract the updated fitness score
        schedule, eval_score, fitness_score, _ = individual_with_fitness
        
        # store with probability initialized to 0 (will be updated by probability() later)
        population.append((schedule, eval_score, fitness_score, 0))
    
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
        # get the actual slot object from the slot_key
        if pa.slot_key[0] == "LEC":
            slot = problem_instance.get_lecture_slot(pa.slot_key)
        else:
            slot = problem_instance.get_tutorial_slot(pa.slot_key)
        
        # get the event object
        event = problem_instance.get_event(pa.event_id)
        
        # assign the event to the slot object (not just the key)
        schedule.assign(event, slot)
    
    # step 2: get all available lecture and tutorial slots objects
    lecture_slots = [problem_instance.get_lecture_slot(key) for key in problem_instance.get_all_lecture_slot_keys()]
    tutorial_slots = [problem_instance.get_tutorial_slot(key) for key in problem_instance.get_all_tutorial_slot_keys()]
    
    # step 3: randomly assign all LECTURES to random LECTURE SLOTS
    for lecture_id in problem_instance.get_all_lecture_ids():
        lecture_event = problem_instance.get_event(lecture_id)
        
        if schedule.is_assigned(lecture_event):
            continue  # already has partial assignment
        
        # pick a completely random lecture slot
        random_slot = random.choice(lecture_slots)
        schedule.assign(lecture_event, random_slot)
    
    # step 4: randomly assign all TUTORIALS to random TUTORIAL SLOTS
    for tutorial_id in problem_instance.get_all_tutorial_ids():
        tutorial_event = problem_instance.get_event(tutorial_id)

        # handle special lectures 851/913
        if tutorial_event.is_special_tut:
            slot_key = ( "TUT", "TU", "18:00" )
            special_slot = problem_instance.get_tutorial_slot(slot_key)
            schedule.assign(tutorial_event, special_slot)
            continue
        
        if schedule.is_assigned(tutorial_event):
            continue  # already has partial assignment
        
        # pick a completely random tutorial slot
        random_slot = random.choice(tutorial_slots)
        schedule.assign(tutorial_event, random_slot)

    return schedule


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
    
    # print eval and fitness statistics
    print(f"\nPopulation fitness statistics:")
    eval_scores = [eval_val for _, eval_val, _, _ in population]
    fitness_scores = [fit_val for _, _, fit_val, _ in population]
    
    print(f"  Eval scores (soft constraints):")
    print(f"    Min: {min(eval_scores):.2f}")
    print(f"    Max: {max(eval_scores):.2f}")
    print(f"    Avg: {sum(eval_scores)/len(eval_scores):.2f}")
    
    print(f"  Fitness scores:")
    print(f"    Min: {min(fitness_scores):.4f}")
    print(f"    Max: {max(fitness_scores):.4f}")
    print(f"    Avg: {sum(fitness_scores)/len(fitness_scores):.4f}")
    
    # check hard constraint violations
    print(f"\nHard constraint violations:")
    for i, (schedule, _, _, _) in enumerate(population):
        valid_penalty = Valid(schedule, problem_instance)
        status = "+ VALID" if valid_penalty == 0 else f" ─ INVALID (penalty: {valid_penalty})"
        print(f"  Schedule {i+1}: {status}")
    
    print(f"{'='*60}\n")


