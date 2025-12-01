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
        #assign_string = str(assign).split()[1]
        #course_num = int(assign_string)

        if assign.is_500_course:
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
    Check NotCompatible(event_a, event_b) constraints
    """
    penalty = 0

    # build event_id -> (day, time) lookup from the current schedule
    event_time = {}
    for event, slot in _iter_assignments(schedule):
        event_time[event.id] = (slot.day, slot.start_time)

    # check all NotCompatible pairs
    for nc in problem.not_compatible:
        a_id = nc.event_a_id
        b_id = nc.event_b_id

        # if one of them isn't assigned, we don't penalize here
        if a_id not in event_time or b_id not in event_time:
            continue

        # if they share the same (day, time), it's a hard violation
        if event_time[a_id] == event_time[b_id]:
            penalty += PEN_HARD

    return penalty


# checks C4 : for all in unwanted, lecture/tutorial should be assigned to ANOTHER slot
def _check_unwanted(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check Unwanted(event, slot) constraints.

    Right now, this DOESN'T penalize if something isn't scheduled... 
    idk if thats riht but
    """
    penalty = 0

    for uw in problem.unwanted:
        event_id = uw.event_id
        slot_key_forbidden = uw.slot_key  

        # look up the event object
        event = problem.get_event(event_id)

        # if the event isn't in the schedule at all, skip
        if not schedule.is_assigned(event):
            continue

        assigned_slot = schedule.get_assignment(event)

        if assigned_slot.slot_key == slot_key_forbidden:
            penalty += PEN_HARD

    return penalty


# checks C3 : for all in partial_assign, should be assigned to specific slots (can be lectures/tutorials)
def _check_partial_assignments(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check PartialAssignment(event, slot) constraints.

    For now, this is a stub that returns 0.
    """
    penalty = 0

    for partial in problem.partial_assignments:
        str_event_id = partial.event_id
        event_id = problem.get_event(str_event_id)

        # check course is in schedule
        if schedule.is_assigned(event_id):
            # check if LEC or TUT
            if partial.slot_key[0] == "LEC":
                partial_slot_key = problem.get_lecture_slot(partial.slot_key)
            else:
                partial_slot_key = problem.get_tutorial_slot(partial.slot_key)

            # check assigned slot matches partial assignment
            assigned_slot_key = schedule.get_assignment(event_id)
            if assigned_slot_key != partial_slot_key:
                penalty += PEN_HARD

        # course is not in schedule, apply penalty
        else:
            penalty += PEN_HARD

    return penalty


# checks C16 : for all in active_learning, lecture/tutorial is assigned to an AL slot
def _check_active_learning_requirements(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    Check Active Learning (AL) requirements:
        - AL-required events must be placed in AL-capable slots.
    """
    penalty = 0
    all_courses = problem.get_all_event_ids()

    # creating a list of all events from the input file
    events = []
    for i in all_courses:
        events.append(problem.get_event(i))

    # check if AL required courses are scheduled at AL slots
    for assign in events:
        if assign.al_required:
            # check if is assigned to a slot, if not apply penalty and continue
            if not schedule.is_assigned(assign):
                penalty += PEN_HARD
                continue

            # if assigned to a slot, check slot is AL, if not apply penalty
            # check if TutorialSlot or LectureSlot AL_max > 0
            # DOES NOT check number of assigned courses to a slot, ONLY if a slot is AL
            slot_key = schedule.get_assignment(assign)
            if isinstance(slot_key, TutorialSlot):
                if slot_key.al_tutorial_max <= 0:
                    penalty += PEN_HARD
            else:
                if slot_key.al_lecture_max <= 0:
                    penalty += PEN_HARD

    return penalty


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
    penalty = 0
    
    # need to check all lectures with "LEC 9" prefix
    # e.g. "CPSC 451 LEC 91 TUT 91"
    for assign in schedule.assignments:
        # parser checks if lecture is an evening event
        if assign.is_evening_event:
            slot_key = schedule.get_assignment(assign)

            # checks if slot is evening time
            if not slot_key.is_evening_slot:
                penalty += PEN_HARD

    # checks if CPSC 851 or CPSC 913 is in appropriate slots
    # and overlaps with any CPSC 351 or CPSC 413
    for assign in schedule.assignments:
        if assign.is_special_tut:

            parts = str(assign).split()
            course, code = parts[0], parts[1]

            # check if evening slot even exists first
            if problem.get_slot(schedule.get_assignment(assign)) is None:
                penalty += PEN_HARD
                continue

            # CPSC 851
            if f"{course} {code}" == "CPSC 851":
                slot_key = schedule.get_assignment(assign)

                # needs to be TUT, TU, 18:00 ONLY
                if (not slot_key.is_evening_slot) or (slot_key.day != "TU") or (not isinstance(slot_key, TutorialSlot)):
                    penalty += PEN_HARD
                    continue

                # check all sections of CPSC 351 TUT/LAB/LEC
                if problem.course_list.get(("CPSC", 351)) is not None:
                    # get list of all CPSC 351 LECs
                    lec_id = problem.course_list.get(("CPSC", 351))

                    for l in lec_id:
                        # checks if lecture is in schedule
                        lec_event = problem.get_event(l)
                        if not schedule.is_assigned(lec_event):
                            continue
                        # Check if the slot is the special slot
                        lec_slot = schedule.get_assignment(lec_event)
                        if lec_slot.start_time == "18:00" and lec_slot.day == "TU":
                            penalty += PEN_HARD

                if problem.tut_list.get(("CPSC", 351)) is not None:
                    # get list of all CPSC 351 TUTs
                    tut_id = problem.tut_list.get(("CPSC", 351))

                    for t in tut_id:
                        # checks if tutorial is in schedule
                        t_event = problem.get_event(t)
                        if not schedule.is_assigned(t_event):
                            continue
                        # Check if the slot is the special slot
                        if schedule.get_assignment(t_event).is_tth_18_19_tutorial:
                            penalty += PEN_HARD
            # CPSC 913
            else:
                slot_key = schedule.get_assignment(assign)

                # needs to be TUT, TU, 18:00 ONLY
                if (not slot_key.is_evening_slot) or (slot_key.day != "TU") or (not isinstance(slot_key, TutorialSlot)):
                    penalty += PEN_HARD
                    continue

                # check all sections of CPSC 413 TUT/LAB/LEC
                if problem.course_list.get(("CPSC", 413)) is not None:
                    # get list of all CPSC 413 LECs
                    lec_id = problem.course_list.get(("CPSC", 413))

                    for l in lec_id:
                        # checks if lecture is in schedule
                        lec_event = problem.get_event(l)
                        if not schedule.is_assigned(lec_event):
                            continue
                        # Check if the slot is the special slot
                        lec_slot = schedule.get_assignment(lec_event)
                        if lec_slot.start_time == "18:00" and lec_slot.day == "TU":
                            penalty += PEN_HARD

                if problem.tut_list.get(("CPSC", 413)) is not None:
                    # get list of all CPSC 413 TUTs
                    tut_id = problem.tut_list.get(("CPSC", 413))

                    for t in tut_id:
                        # checks if tutorial is in schedule
                        t_event = problem.get_event(t)
                        if not schedule.is_assigned(t_event):
                            continue
                        # Check if the slot is the special slot
                        if schedule.get_assignment(t_event).is_tth_18_19_tutorial:
                            penalty += PEN_HARD

    return penalty

# checks C6 : department blackout
def _check_department_blackout(schedule: Schedule, problem: ProblemInstance) -> int:
    """
    C6: No lectures are allowed in slot (TU, 11:00).

    Note: parser already enforces allowed days/times for lecture slots,
    but if a forbidden slot exists in the input, this double-checks that
    no lecture is actually assigned there.
    """
    penalty = 0

    for event, slot in _iter_assignments(schedule):
        if event.is_lecture() and slot.day == "TU" and slot.start_time == "11:00":
            penalty += PEN_HARD

    return penalty



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
    penalty += _check_department_blackout(schedule, problem)
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