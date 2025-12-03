import random
from .schedule import Schedule
from parser.event import Event
from parser.constants import *

# note: for extension functions, do we want to consider if the tutorial/lecture has already filled up? is there a counter to how many events we've assigned to the slots


# function to mutate a schedule by randomly changing a single evening event's slot assignment
# f: Schedule to mutate
# slots: list of all available slots
# returns the mutated Schedule
def mutate_evening(f, slots):
    # creating a copy of the schedule to mutate
    f_prime = Schedule(assignments=f.assignments.copy())
    
    # finding all evening events in the schedule
    evening_events = [e for e in f_prime.assignments if e.is_evening_event]
    # if there are no evening events, return the None (can't mutate), avoiding returning the same schedule
    if not evening_events:
        return None

    # select a random evening event to mutate
    mutated_event = random.choice(evening_events)
    # get the current slot assignment of the evening event
    current_slot = f_prime.get_assignment(mutated_event)

    # finding all the evening slots of the same kind (lecture/tutorial) that are different from the current slot
    evening_slots = [s for s in slots
        if (s.is_evening_slot)
        and (s.kind == mutated_event.kind)
        and (s != current_slot)
    ]
    # if there are no alternative evening slots, return the None (can't mutate), avoiding returning the same schedule
    if not evening_slots:
        return None

    # otherwise, we can assign a new random evening slot to the mutated event
    f_prime.assign(mutated_event, random.choice(evening_slots))

    # return the mutated schedule
    return f_prime


# function to mutate a schedule by randomly changing a single active learning event's slot assignment
# f: Schedule to mutate
# slots: list of all available slots
# returns the mutated Schedule
def mutate_AL(f, slots):
    # creating a copy of the schedule to mutate
    f_prime = Schedule(assignments=f.assignments.copy())
    
    # finding all active learning required events in the schedule
    al_events = [e for e in f_prime.assignments if e.al_required]
    # if there are no active learning events, return the original schedule (can't mutate), avoiding returning the same schedule
    if not al_events:
        return None

    # select a random active learning event to mutate
    mutated_event = random.choice(al_events)
    # get the current slot assignment of the active learning event
    current_slot = f_prime.get_assignment(mutated_event)

    # finding all the active learning slots of the same kind (lecture/tutorial) that are different from the current slot
    al_slots = [s for s in slots
        if (
            (mutated_event.kind == EVENT_KIND_LECTURE and s.kind == EVENT_KIND_LECTURE)
            or (mutated_event.kind in TUTORIAL_TYPES and s.kind in TUTORIAL_TYPES)
        )
        and (
            (s.kind == EVENT_KIND_LECTURE and s.al_lecture_max > 0)
            or (s.kind in TUTORIAL_TYPES and s.al_tutorial_max > 0)
        )
        and (s != current_slot)
    ]
    # if there are no alternative active learning slots, return the original schedule (can't mutate), avoiding returning the same schedule
    if not al_slots:
        return None

    # otherwise, we can assign a new random active learning slot to the mutated event
    f_prime.assign(mutated_event, random.choice(al_slots))

    # return the mutated schedule
    return f_prime


# function to mutate a schedule by randomly changing a single lecture event's slot assignment
# f: Schedule to mutate
# slots: list of all available slots
# returns the mutated Schedule
def mutate_lecture(f, slots):
    # creating a copy of the schedule to mutate
    f_prime = Schedule(assignments=f.assignments.copy())
    
    # find all lecture events in the schedule
    lecture_events = [e for e in f_prime.assignments if e.is_lecture()]
    # if there are no lecture events, return the original schedule (can't mutate), avoiding returning the same schedule
    if not lecture_events:
        return None

    # select a random lecture event to mutate
    mutated_event = random.choice(lecture_events)
    # get the current slot assignment of the lecture event
    current_slot = f_prime.get_assignment(mutated_event)

    # find all lecture slots that are different from the current slot
    lecture_slots = [s for s in slots if (s.kind == EVENT_KIND_LECTURE) and (s != current_slot)]
    # if there are no alternative lecture slots, return the original schedule (can't mutate), avoiding returning the same schedule
    if not lecture_slots:
        return None

    # otherwise, we can assign a new random lecture slot to the mutated event
    f_prime.assign(mutated_event, random.choice(lecture_slots))

    # return the mutated schedule
    return f_prime

# function to mutate a schedule by randomly changing a single tutorial event's slot assignment
# f: Schedule to mutate
# slots: list of all available slots
# returns the mutated Schedule
def mutate_tutorial(f, slots):
    # creating a copy of the schedule to mutate
    f_prime = Schedule(assignments=f.assignments.copy())
    
    # find all tutorial events in the schedule
    tutorial_events = [e for e in f_prime.assignments if e.is_tutorial()]
    # if there are no tutorial events, return the original schedule (can't mutate), avoiding returning the same schedule
    if not tutorial_events:
        return None

    # select a random tutorial event to mutate
    mutated_event = random.choice(tutorial_events)
    # get the current slot assignment of the tutorial event
    current_slot = f_prime.get_assignment(mutated_event)

    # find all tutorial slots that are different from the current slot
    tutorial_slots = [s for s in slots if (s.kind in TUTORIAL_TYPES) and (s != current_slot)]
    # if there are no alternative tutorial slots, return the original schedule (can't mutate), avoiding returning the same schedule
    if not tutorial_slots:
        return None

    # otherwise, we can assign a new random tutorial slot to the mutated event
    f_prime.assign(mutated_event, random.choice(tutorial_slots))

    # return the mutated schedule
    return f_prime

# function to produce a child schedule from two parent schedules (crossover extension rule)
# f_a: first parent schedule
# f_b: second parent schedule
# returns the child schedule resulting from crossover of two parents
def crossover(f_a, f_b):
    # creating a new Schedule object for the child
    f_c = Schedule()

    # iterating through each event
    for e in f_a.assignments:
        # randomly assigning the event's slot from one of the parents
        if random.choice([True, False]):
            f_c.assign(e, f_a.get_assignment(e))
        else:
            f_c.assign(e, f_b.get_assignment(e))

    # returning the child schedule
    return f_c


# function to purge the bottom k schedules from a population
# population: list of (schedule, fitness) tuples
# k: number of schedules to purge
# returns the purged population
def purge(population, k):

    # if the k value is less than or equal to 0, return the original population (don't purge anything)
    if k <= 0:
        return population

    # if the k value is greater than or equal to the population size, return an empty list (purge everything)
    if k >= len(population):
        return []

    # sort population by fitness (ascending)
    population.sort(key=lambda x: x[1])

    # return population without the bottom k schedules
    return population[k:]
