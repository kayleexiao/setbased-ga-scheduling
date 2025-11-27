"""
hard_constraints.py

Implements the hard constraints lol

All private internal helpers start with _

DEFINITIONS:
    - `schedule`: a Schedule object (mapping Event -> Slot)
    - `problem`: a ProblemInstance containing all events, slots, and constraints


"""

from typing import Tuple, Dict

from model.schedule import Schedule
from parser.problem_instance import ProblemInstance

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
    return a list of Event objects that are assigned to the given slot_key.

    slot_key: a 3-tuple (kind, day, start_time), e.g. ('LEC', 'MO', '8:00')

    NOTE: For now this is a stub that returns an empty list.
    """
    # TODO (Step 2): implement this by scanning schedule.assignments
    return []


# ---------------------------------------------------------------------------
# constraint-specific checkers
#  - these all return integer penalties, but they are stubbed at 0 for now
# ---------------------------------------------------------------------------

def _check_capacity(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check lecture/tutorial and Active Learning capacity constraints. (No too many classes in one slot)

    for now, this is a stub that returns 0.
    in later steps, this will enforce:
        - lecture_max / tutorial_max
        - al_lecture_max / al_tutorial_max
    """
    # TODO: implement
    return 0


def _check_not_compatible(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check NotCompatible(event_a, event_b) constraints.

    For now, this is a stub that returns 0.
    Later, this will ensure not-compatible events are not at the same time.
    """
    # TODO: implement
    return 0


def _check_unwanted(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check Unwanted(event, slot) constraints.

    For now, this is a stub that returns 0.
    """
    # TODO: implement
    return 0


def _check_partial_assignments(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check PartialAssignment(event, slot) constraints.

    For now, this is a stub that returns 0.
    """
    # TODO: implement
    return 0


def _check_active_learning_requirements(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check Active Learning (AL) requirements:
        - AL-required events must be placed in AL-capable slots.

    For now, this is a stub that returns 0.
    """
    # TODO: implement
    return 0


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