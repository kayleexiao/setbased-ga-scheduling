import random
from model.schedule import Schedule
from parser.slot import LectureSlot, TutorialSlot
from parser.constants import TUTORIAL_TYPES


def repair_schedule(schedule: Schedule, problem):
    """
    Repair a schedule w.r.t. some hard constraints:

    1. evening lectures into evening slots
    2. cpsc 851/913 slot
    3. tutorial cant share slot with lecture of same course
    4. ensuring each slot has only 1 5xx course
    5. non-compatible
    6. capacity violations
     
    """
    # -----------------------------
    # 1. Force evening lectures into evening lecture slots
    # -----------------------------

    # Collect all slots marked as evening lecture slots
    evening_lec_slots = [
        s for s in problem.lec_slots_by_key.values()
        if getattr(s, "is_evening_slot", False)
    ]

     # Iterate over all assigned events
    for event in list(schedule.assignments.keys()):

         # Check if this event is an evening lecture
        if getattr(event, "is_evening_event", False):

            # Get event's assigned slot
            slot = schedule.get_assignment(event)

            # If its not placed in an evening slot, fix it
            if not getattr(slot, "is_evening_slot", False):

                # Move it into a valid evening slot
                if evening_lec_slots:
                    schedule.assign(event, random.choice(evening_lec_slots))

    # -----------------------------
    # 2. Force cpsc851/913 tuts into tu 18:00
    # -----------------------------

    # Find the required tutorial slot
    tu_18_tut = [
        s for s in problem.tut_slots_by_key.values()
        if s.day == "TU" and s.start_time == "18:00"
    ]
    target_tu_18 = tu_18_tut[0] if tu_18_tut else None

    # If this slot exists, enforce it for special tutorials
    if target_tu_18:
        for ev in list(schedule.assignments.keys()):

            # Identify special tutorials
            if getattr(ev, "is_special_tut", False):

                # Get assigned slot
                slot = schedule.get_assignment(ev)

                # If not currently in TU 18:00, fix it
                if not (
                    isinstance(slot, TutorialSlot)
                    and slot.day == "TU"
                    and slot.start_time == "18:00"
                ):
                    schedule.assign(ev, target_tu_18)

    # -----------------------------
    # 3. Fix tutorial share slot with lecture of same course
    # -----------------------------

    # Build mapping
    # course -> set of (day,time) where lectures occur
    lec_slots_by_course = {}
    for course_key, lec_ids in problem.course_list.items():
        tset = set()

        # Check each lecture's assigned slot
        for lec_id in lec_ids:
            lec_ev = problem.get_event(lec_id)
            if schedule.is_assigned(lec_ev):
                s = schedule.get_assignment(lec_ev)
                tset.add((s.day, s.start_time))
        lec_slots_by_course[course_key] = tset

    # Collect all tutorial slots for reassignments
    all_tut_slots = list(problem.tut_slots_by_key.values())

    # Try fixing each tutorial
    for course_key, tut_ids in problem.tut_list.items():
        forbidden = lec_slots_by_course.get(course_key, set())
        if not forbidden:
            continue

        for tut_id in tut_ids:
            tut_ev = problem.get_event(tut_id)

            # Skip if not assigned
            if not schedule.is_assigned(tut_ev):
                continue

            slot = schedule.get_assignment(tut_ev)
            time = (slot.day, slot.start_time)

            # If tutorial shares a slot with its lecture, fix it
            if time in forbidden:
                # pick a non-conflicting tutorial slot
                candidates = [s for s in all_tut_slots if (s.day, s.start_time) not in forbidden]
                if candidates:
                    schedule.assign(tut_ev, random.choice(candidates))


    # -----------------------------
    # 4. Fix 5xx conflicts
    # Ensure each slot has at most one 5xx lec
    # -----------------------------

    # Map slot_key to list of 500-level lectures in that slot
    slot_to_5xx = {}
    for ev, sl in schedule.assignments.items():
        if ev.is_500_course and ev.is_lecture():
            slot_to_5xx.setdefault(sl.slot_key, []).append((ev, sl))

    # Now fix any slot that has 2 or more 500-level lectures
    all_lec_slots = list(problem.lec_slots_by_key.values())

    # List of all lecture slots for relocation
    for slot_key, items in slot_to_5xx.items():
        if len(items) <= 1:
            # no conflict
            continue  

        # Keep one
        keep_ev, keep_sl = items[0]

        # Move the rest
        for ev_to_move, original_slot in items[1:]:

            # Build list of alternative slots
            candidates = []
            for s in all_lec_slots:

                # Skip same slot
                if s.slot_key == slot_key: 
                    continue

                # Evening constraints
                if ev_to_move.is_evening_event and not getattr(s, "is_evening_slot", False):
                    continue

                # AL constraints
                if ev_to_move.al_required and getattr(s, "al_lecture_max", 0) == 0:
                    continue

                candidates.append(s)

            # Make the move if possible
            if candidates:
                new_slot = random.choice(candidates)
                schedule.assign(ev_to_move, new_slot)


    # -----------------------------
    # 5. Fix non-compatible pairs
    # If two events are not compatible and share same slot, move onr of them to a compatible alternative slot
    # -----------------------------

    for nc in problem.not_compatible:

        # Get the 2 events involved
        evA = problem.get_event(nc.event_a_id)
        evB = problem.get_event(nc.event_b_id)

        # Skip if either isnt scheduled
        if not (schedule.is_assigned(evA) and schedule.is_assigned(evB)):
            continue

        sA = schedule.get_assignment(evA)
        sB = schedule.get_assignment(evB)

        # Make sure they actually conflict before we fix them
        if (sA.day != sB.day) or (sA.start_time != sB.start_time):
            continue

        # Randomly choose one to move
        ev_to_move = random.choice([evA, evB])
        old_slot = schedule.get_assignment(ev_to_move)

        # Select a slot type
        if ev_to_move.is_lecture():
            all_slots = list(problem.lec_slots_by_key.values())
        else:
            all_slots = list(problem.tut_slots_by_key.values())

        # Build list of valid alternative slots
        candidates = []
        for s in all_slots:

            # Skip same slot it was in before
            if (s.day == old_slot.day and s.start_time == old_slot.start_time):
                continue

            # Evening restriction
            if ev_to_move.is_lecture() and ev_to_move.is_evening_event and not getattr(s, "is_evening_slot", False):
                continue

            # AL restriction
            if ev_to_move.is_lecture() and ev_to_move.al_required and getattr(s, "al_lecture_max", 0) == 0:
                continue

            candidates.append(s)

        # Make the move if possible
        if candidates:
            schedule.assign(ev_to_move, random.choice(candidates))

    # -----------------------------
    # 6. Capacity violations
    # -----------------------------

    # ----- Lecture slots -----
    for slot in problem.lec_slots_by_key.values():

        # All events in this slot
        events_here = [
            ev for ev, sl in schedule.assignments.items()
            if sl.slot_key == slot.slot_key
        ]

        # Filter lectures assigned here
        lectures = [e for e in events_here if e.is_lecture()]
        AL_lectures = [e for e in lectures if e.al_required]

        # Get the overflow counts
        overflow = max(0, len(lectures) - slot.lecture_max)
        overflow_AL = max(0, len(AL_lectures) - slot.al_lecture_max)

        # Randomly pick events to move out
        to_move = random.sample(lectures, overflow) + random.sample(AL_lectures, overflow_AL)

        # Move each overflowing event
        for ev_to_move in to_move:
            candidates = []

            # Find valid lecture slot alternatives
            for s in problem.lec_slots_by_key.values():

                # Skip same slot it was in before
                if s.slot_key == slot.slot_key:
                    continue

                # Evening restrictions
                if ev_to_move.is_evening_event and not getattr(s, "is_evening_slot", False):
                    continue

                # AL restrictions
                if ev_to_move.al_required and getattr(s, "al_lecture_max", 0) == 0:
                    continue
                candidates.append(s)

            # Make the move if possible
            if candidates:
                schedule.assign(ev_to_move, random.choice(candidates))

    # ----- Tutorial slots ------
    for slot in problem.tut_slots_by_key.values():

        # All events in this slot
        events_here = [
            ev for ev, sl in schedule.assignments.items()
            if sl.slot_key == slot.slot_key
        ]

        tutorials = [e for e in events_here if e.is_tutorial()]
        AL_tutorials = [e for e in tutorials if e.al_required]

        overflow = max(0, len(tutorials) - slot.tutorial_max)
        overflow_AL = max(0, len(AL_tutorials) - slot.al_tutorial_max)

        to_move = random.sample(tutorials, overflow) + random.sample(AL_tutorials, overflow_AL)

        for ev_to_move in to_move:
            candidates = []
            for s in problem.tut_slots_by_key.values():
                if s.slot_key == slot.slot_key:
                    continue
                candidates.append(s)

            if candidates:
                schedule.assign(ev_to_move, random.choice(candidates)) 

    return schedule
