"""
hard_constraints.py

Implements the hard constraints lol

All private internal helpers start with _

DEFINITIONS:
    - `schedule`: a Schedule object (mapping Event -> Slot)
    - `problem`: a ProblemInstance containing all events, slots, and constraints

LIST OF ALL HARD CONSTRAINTS:
LECTURE CONSTRAINTS
    - C1 : no more than lecture_max assigned to a lecture slot
    - C2 : for all in notcompatible, they are assigned to different slots (can be lecture/tutorials)
    - C3 : for all in partial_assign, should be assigned to specific slots (can be lectures/tutorials)
    - C4 : for all in unwanted, lecture/tutorial should be assigned to ANOTHER slot
    - C5 : for all 5XX lectures, they should be scheduled into different slots
        - a slot should only have ONE 5XX course

    - C6 : no lectures are assigned on slot (Tu, 11:00)
    - C7 : lectures should occupy blocks Mo/We/Fr, or Tu/Th
        - handled by parser?

TUTORIAL CONSTRAINTS
    - C8 : no more than tutorial_max assigned to a tutorial slot
    - C9 : for all tutorials, should be booked in a DIFFERENT slot than lecture of same section

    - C10 : tutorials should occupy blocks Mo/We, or Tu/Th, or Fr
        - handled by parser?

EVENING CONSTRAINTS
    - C11 : for all lectures with prefix "DIV 9", assigned to a slot 18:00 or later
    - C12 : CPSC 851 is scheduled at (Tu, 18:00) AND no overlap with CPSC 351
        - class will exist if CPSC 351 exists
    - C13 : CPSC 913 is scheudled at (Tu, 18:00) AND no overlap with CPSC 413
        - class will exist if CPSC 413 exists

AL CONSTRAINTS
    - C14 : no more than al_lecture_max assigned to a lecture slot
    - C15 : no more than al_tutorial_max assigned to a tutorial slot
    - C16 : for all in active_learning, lecture/tutorial is assigned to an AL slot
"""

from typing import Tuple, Dict
from collections import defaultdict

from model.schedule import Schedule
from parser.problem_instance import ProblemInstance
from parser.slot import LectureSlot, TutorialSlot

# this is the base penalty for hard-constraint violation but we'll later tie it to command line args
PEN_HARD = 1


SlotKey = Tuple[str, str, str]

# -----------------
# LOW LEVEL HELPERS (currently just stubs rn)
# -----------------


def _iter_assignments(schedule: Schedule):
    """
    this yields (event, slot) pairs for each event assigned in this schedule
    """
    return schedule.assignments.items()


def _events_in_slot(schedule: Schedule, slot_key: SlotKey):
    """
    Returns all events assigned to a given slot

    Example:
        slot_key = ('LEC', 'MO', '8:00')

        If the schedule has:
            CPSC 231 LEC -> ('LEC', 'MO', '8:00')
            CPSC 331 LEC -> ('LEC', 'MO', '8:00')

        This function returns:
            [CPSC 231 LEC, CPSC 331 LEC]

    """
    events = []

    for event, slot in _iter_assignments(schedule):
        if slot.slot_key == slot_key:
            events.append(event)

    return events


# ---------------------------------------------------------------------------
# constraint-specific checkers
#  - these all return integer penalties, but they are stubbed at 0 for now
# ---------------------------------------------------------------------------
# checks C1 : no more than lecture_max assigned to a lecture slot
#   - C8 : no more than tutorial_max assigned to a tutorial slot
#   - C14 : no more than al_lecture_max assigned to a lecture slot
#   - C15 : no more than al_tutorial_max assigned to a tutorial slot
def _check_capacity(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check lecture/tutorial AND Active Learning capacity constraints. (Not too many classes in one slot)
    - aka lecture_max, tutorial_max, al_lecture_max and al_tutorial_max

    Returns how many hard constraint violations occured
    """
    penalty = 0

    # lecture slot capacity
    for slot_key, slot in problem.lec_slots_by_key.items():

        events_here = _events_in_slot(schedule, slot_key)

        # checks how many lectures are in this slot
        total_lectures = sum(1 for e in events_here if e.is_lecture())

        # how many require active learning
        al_lectures = sum(1 for e in events_here if e.is_lecture() and e.al_required)

        # actual capacity check
        if total_lectures > slot.lecture_max:
            penalty += PEN_HARD * (total_lectures - slot.lecture_max)

        # capacity check for AL
        if al_lectures > slot.al_lecture_max:
            penalty += PEN_HARD * (al_lectures - slot.al_lecture_max)

    # tutorial slot capcity
    for slot_key, slot in problem.tut_slots_by_key.items():

        events_here = _events_in_slot(schedule, slot_key)

        total_tutorials = sum(1 for e in events_here if e.is_tutorial())

        al_tutorials = sum(1 for e in events_here if e.is_tutorial() and e.al_required)

        if total_tutorials > slot.tutorial_max:
            penalty += PEN_HARD * (total_tutorials - slot.tutorial_max)

        if al_tutorials > slot.al_tutorial_max:
            penalty += PEN_HARD * (al_tutorials - slot.al_tutorial_max)

    return penalty


# checks C5 : for all 5XX lectures, they should be scheduled into different slots
#       - a slot should only have ONE 5XX course
def _check_5xx_lecures(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Iterates through ALL 5XX lectures in the schedule to make sure if each is assigned to a different slot
    """
    penalty = 0
    lecture5xx_by_slot_key = {}

    for assign in schedule.assignments:
        # isolating lecture number in each assignment and adding to lecture5XX_by_slot_key
        assign_string = str(assign).split()[1]
        course_num = int(assign_string)

        if course_num >= 500:
            slot_key = schedule.get_assignment(assign)
            lecture5xx_by_slot_key[slot_key] = lecture5xx_by_slot_key.get(slot_key, 0) + 1

            # if more than one 5XX lecture is scheduled in the same slot, apply penalty
            if lecture5xx_by_slot_key[slot_key] > 1:
                penalty += PEN_HARD

    return penalty


# checks C9 : for all tutorials, should be booked in a DIFFERENT slot than lecture of same section
def _check_tutorials_section_diff_from_lecture(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check same section tutorial is assigned to a different slot than its lecture
    Example: CPSC 231 LEC 01 TUT 01 -> Mo, 10:00
             CPSC 231 LEC 01        -> Mo, 10:00
    Group together all lectures/tutorials in same section, then look at their slots
    """
    penalty = 0
    tut_to_lec = defaultdict(list)

    # create mapping from section to all the courses in the same section in the schedule
    for assign in schedule.assignments:

        if "LEC" in str(assign):

            split_assign = str(assign).split()
            # creating key to tut_to_lec to group all same section courses
            # key = COURSE NUMBER "LEC" SEC_NUM
            # assign = Event(id='CPSC 231 LEC 02', kind='LEC', al_required=True)
            key = f"{split_assign[0]} {split_assign[1]} {split_assign[2]} {split_assign[3]}"

            # have to convert from LectureSlot(day='TU', time='9:30', max=2) to just TU, 9:30
            #time_slot = str(schedule.get_assignment(assign))
            time_slot = schedule.get_assignment(assign)

            tut_to_lec[key].append(time_slot)


    # go through all the courses with the same section
    for section, slots in tut_to_lec.items():
        if len(slots) <= 1:
            continue
        else:
            lec = [s for s in slots if isinstance(s, LectureSlot)]
            tut = [s for s in slots if isinstance(s, TutorialSlot)]

            # only tutorials at time slot
            if not lec:
                continue
            else:
                # check each lecture and tutorial in same section
                for l in lec:
                    for t in tut:
                        # assigned to same slot = add penalty
                        if (l.day == t.day) and (l.start_time == t.start_time):
                            # conflict between lecture day/time and tutorial day/time
                            penalty += PEN_HARD

    return penalty


# checks C2 : for all in notcompatible, they are assigned to different slots (can be lecture/tutorials)
def _check_not_compatible(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check NotCompatible(event_a, event_b) constraints.

    For now, this is a stub that returns 0.
    Later, this will ensure not-compatible events are not at the same time.
    """
    # TODO: implement
    return 0


# checks C4 : for all in unwanted, lecture/tutorial should be assigned to ANOTHER slot
def _check_unwanted(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check Unwanted(event, slot) constraints.

    For now, this is a stub that returns 0.
    """
    # TODO: implement
    return 0


# checks C3 : for all in partial_assign, should be assigned to specific slots (can be lectures/tutorials)
def _check_partial_assignments(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check PartialAssignment(event, slot) constraints.

    For now, this is a stub that returns 0.
    """
    # TODO: implement
    return 0


# checks C16 : for all in active_learning, lecture/tutorial is assigned to an AL slot
def _check_active_learning_requirements(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check Active Learning (AL) requirements:
        - AL-required events must be placed in AL-capable slots.

    For now, this is a stub that returns 0.
    """
    # TODO: implement
    return 0


# checks C11 : for all lectures with prefix "DIV 9", assigned to a slot 18:00 or later
#   - C12 : CPSC 851 is scheduled at (Tu, 18:00) AND no overlap with CPSC 351
#        - class will exist if CPSC 351 exists
#    - C13 : CPSC 913 is scheudled at (Tu, 18:00) AND no overlap with CPSC 413
#        - class will exist if CPSC 413 exists
def _check_evening_rules(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check evening-related hard constraints:
        - evening lectures in evening slots,
        - 500-level lectures not in forbidden slots,
        - special tutorials in the correct Tu/Th evening slot.

    For now, this is a stub that returns 0.
    """
    # TODO: implement in later step
    return 0


# ------------
# Public API 
# ------------

def Valid(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Valid(schedule) - MAIN hard constraint function that adds up all hard constraint violations

    If it returns:
    0 -> its perfect (no hard rules broken)
    else -> invalid schedule
    """
    penalty = 0
    penalty += _check_capacity(schedule, problem)
    penalty += _check_not_compatible(schedule, problem)
    penalty += _check_unwanted(schedule, problem)
    penalty += _check_partial_assignments(schedule, problem)
    penalty += _check_active_learning_requirements(schedule, problem)
    penalty += _check_evening_rules(schedule, problem)

    penalty += _check_5xx_lecures(schedule, problem)
    penalty += _check_tutorials_section_diff_from_lecture(schedule, problem)
    return penalty


def PassLectures(schedule: Schedule, problem: ProblemInstance) -> bool:
    """
    Returns True if the schedule passes all hard constraints
    related to lectures.

    Right now: just checks if the WHOLE schedule is valid.
    """
    return Valid(schedule, problem) == 0


def PassTutorials(schedule: Schedule, problem: ProblemInstance) -> bool:
    """
    Returns True if the schedule passes all hard constraints
    related to tutorials.

    Right now: just checks if the WHOLE schedule is valid.
    """
    return Valid(schedule, problem) == 0


def PassAL(schedule: Schedule, problem: ProblemInstance) -> bool:
    """
    Returns True if all Active Learning (AL) rules are satisfied.
    """
    return _check_active_learning_requirements(schedule, problem) == 0


def PassEvening(schedule: Schedule, problem: ProblemInstance) -> bool:
    """
    Returns True if all evening-related rules are satisfied.
    """
    return _check_evening_rules(schedule, problem) == 0