
# Eval function takes in one schedule to output int value of SOFT constraints
# minimize eval to 0 to pass all soft constraints
# summation of four eval sub functions
# problem : ProblemInstance
# use event_id to get Event object to use to find assignment in schedule
def eval(schedule, problem) -> int:
    penalty = 0

    penalty += (eval_minfilled(schedule, problem) * problem.w_minfilled)  # check lecture and tutorial min

    penalty += (eval_pref(schedule, problem) * problem.w_pref)   # checks to see if lecture/tutorial are assigned to pref slot

    penalty += (eval_secdiff(schedule, problem) * problem.w_secdiff)  # check same sections of LECTURES are assigned to same slot

    penalty += (eval_pair(schedule, problem) * problem.w_pair)   # checks if 2 lectures/tutorials are scheduled at the same time

    return penalty


# sub eval function for minimum number of lectures/tutorials that should be at slot
# multiplicative for max(0, min_at_slot - assigned_at_slot)
def eval_minfilled(schedule, problem) -> int:
    min_penalty = 0
    # go through all lectures and tutorials and add them up
    tut_count, lec_count = {}, {}

    # sort through all assignments to either lecture count or tutorial count
    for assign in schedule.assignments:
        # e.g. assign = CPSC 231 LEC 01
        slot_key = str(schedule.get_assignment(assign))
        slot_day, slot_time = slot_key.replace(",", "").strip().split()

        # increment for every lecture or tutorial slot
        if "TUT" in str(assign):
            tut_slot_key = ("TUT", slot_day, slot_time)
            tut_count[tut_slot_key] = tut_count.get(tut_slot_key, 0) + 1
        # LAB treated as TUT in TutorialSlot.kind
        elif "LAB" in str(assign):
            lab_slot_key = ("TUT", slot_day, slot_time)
            tut_count[lab_slot_key] = tut_count.get(lab_slot_key, 0) + 1
        else:
            lec_slot_key = ("LEC", slot_day, slot_time)
            lec_count[lec_slot_key] = lec_count.get(lec_slot_key, 0) + 1
    

    # iterate through lecture slots by their keys to see their min
    # compare to assigned slots to see diff in lecture min and assigned lectures to slot
    for lec in problem.lec_slots_by_key:
        # e.g. lec = ('LEC', 'MO', '8:00')
        min = problem.lec_slots_by_key[lec].lecture_min

        # lectures are assigned to slot, then see how many compared to min required
        if lec in lec_count:
            min_penalty += (problem.pen_lecturemin * max(0, (min - lec_count[lec])))
        # no lectures assigned to slot
        else:
            min_penalty += (problem.pen_lecturemin * max(0, min))

    for tut in problem.tut_slots_by_key:
        min = problem.tut_slots_by_key[tut].tutorial_min

        if tut in tut_count:
            min_penalty += (problem.pen_tutorialmin * max(0, (min - tut_count[tut])))
        else:
            min_penalty += (problem.pen_tutorialmin * max(0, min))

    return min_penalty


# Uses individual pen_pref value in section["Preferences"] -> problemInstance
# sub eval function for preference of classes deviating from preferred slot
def eval_pref(schedule, problem) -> int:
    pref_penalty = 0

    # check each preference in ProblemInstance
    for pref in problem.preferences:
        # e.g. pref = Preference(event='CPSC 231 LEC 01', slot=('LEC', 'TU', '9:30'), value=10)
        event_id = pref.event_id
        slot_key = pref.slot_key

        # get event object using event id from appropriate list
        if "TUT" in event_id or "LAB" in event_id:
            event = problem.tut_by_id[event_id]
        else:
            event = problem.lec_by_id[event_id]

        # event id is not scheduled 
        # skip or add penalty value if not scheduled?
        if not schedule.is_assigned(event):
            continue
        
        # checks preferred slot with actual assigned slot
        # formats slot_key to <DAY>, <TIME>
        formatted_key = format_slot_keys(slot_key)

        # converts (schedule.get_assignment(event)) to str for comparison
        if str(schedule.get_assignment(event)) != formatted_key:
            pref_penalty += pref.value

    return pref_penalty


# sub eval function to get penalty for same sections in same slots 
# (applied once for overlapping sections)
def eval_secdiff(schedule, problem) -> int:
    sec_penalty = 0

    # store all lectures with the same section, increment for each same section detected
    same_section = {}

    # remove TUT and LAB
    # fill in same_section dict with lectures of the same lecture
    for assign in schedule.assignments:
        # e.g. assign = CPSC 231 LEC 01
        # ignore TUT and LAB assignments in schedule
        if "TUT" in str(assign) or "LAB" in str(assign):
            continue

        # keys for same_section dict
        # DAY, TIME
        slot_key = str(schedule.get_assignment(assign))
        
        # combine same sections into one tuple of identifier and slot
        # e.g. ('CPSC 231 LEC', 'TU, 9:30')
        # ('CPSC 231 LEC', 'TU, 9:30')
        assign_key = " ".join(str(assign).split()[:3])
        key = (assign_key, slot_key)

        # increment for each of same section
        same_section[key] = same_section.get(key, 0) + 1
    
    # add penalty for each section in same slot
    # MAYBE: change to multiplicative penalty if several sections in same slot?
    for (assign_key, slot_key), count in same_section.items():
        if count > 1:
            sec_penalty += (problem.pen_section * count)

    return sec_penalty


# sub eval function to get eval value for each pair of lectures/tutorials not assigned to same slot
def eval_pair(schedule, problem) -> int:
    pair_penalty = 0

    # check pairs to see if assigned slots are same
    for pair in problem.pairs:
        event_a_id = pair.event_a_id
        event_b_id = pair.event_b_id

        # get event object from event id from appropriate list
        if "TUT" in event_a_id or "LAB" in event_a_id:
            event_a = problem.tut_by_id[event_a_id]
        else:
            event_a = problem.lec_by_id[event_a_id]

        # get event object from event id from appropriate list
        if "TUT" in event_b_id or "LAB" in event_b_id:
            event_b = problem.tut_by_id[event_b_id]
        else:
            event_b = problem.lec_by_id[event_b_id]

        # skip if either event is not assigned in schedule
        if not schedule.is_assigned(event_b) or not schedule.is_assigned(event_a):
            continue

        # see if both slots are the same
        if schedule.get_assignment(event_a) != schedule.get_assignment(event_b):
            pair_penalty += problem.pen_notpaired

    return pair_penalty


# helper function to format slot keys to "DAY, TIME"
def format_slot_keys(slot_key):
    kind, day, time = slot_key

    return f"{day}, {time}"