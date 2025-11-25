# Section headers from input file
SECTION_HEADERS = [
    "Name:",
    "Lecture slots:",
    "Tutorial slots:",
    "Lectures:",
    "Tutorials:",
    "Not compatible:",
    "Unwanted:",
    "Preferences:",
    "Pair:",
    "Partial assignments:",
]

# Reads raw input and returns a list of strings
# Each string is one line from the file
def read_all_lines(path: str) -> list[str]:
    with open(path, "r") as f:
        # Strip whitespace and newline characters from each line
        return [line.strip() for line in f.readlines()]


# Takes list produced by read_all_lines() and divides it into a
# dictionary of sections.
def split_into_sections(lines: list[str]) -> dict[str, list[str]]:
    # Final output dictionary
    sections = {} 
    # Keeps track of what section we are in
    current_header = None
    # Collects lines in current section
    buffer = []

    # Main loop
    for line in lines:

        if line in SECTION_HEADERS:

            if current_header is not None:
                sections[current_header] = buffer

            # Init new section
            current_header = line
            # Prepare buffer
            buffer = []

        else:
            # Collect all lines in current section
            if current_header is not None and line != "":
                buffer.append(line)
    
    # Save last buffered section
    if current_header is not None:
        sections[current_header] = buffer
    
    return sections

# Helper to convert lower case in input to python bool
def parse_bool(text: str) -> bool:
    t = text.strip().lower()

    if t == "true":
        return True
    if t == "false":
        return False
    
# Parse non compatible constraints
# Returns list of dicts {event_a_id: "event a", event_b_id: "event b"}
def parse_not_compatible(lines, events_by_id):
    
    not_compatible_list = []

    for line in lines:
        if not line.strip():
            continue
         
        parts = [p.strip() for p in line.split(",")]
        event_a_id, event_b_id = parts

        if event_a_id not in events_by_id:
            raise ValueError(f"Unknown event in 'Not Compatible:' {event_a_id}")
        if event_b_id not in events_by_id:
            raise ValueError(f"Unknown event in 'Not Compatible:' {event_b_id}")
         
        not_compatible_list.append({
            "event_a_id": event_a_id,
            "event_b_id": event_b_id
        })

    return not_compatible_list

# Parse unwanted time constraints 
# Returns list of dicts {event_id, slot_key}
def parse_unwanted(lines, events_by_id, lec_slot_index, tut_slot_index):

    unwanted_list = []

    for line in lines:
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        event_id, day, start_time = parts

        if event_id not in events_by_id:
            raise ValueError(f"Unknown event in 'Unwanted:' {event_id}")
        
        event_obj = events_by_id[event_id]

        if event_obj.kind == "LEC":
            key = lec_slot_index.get((day, start_time))
        else:
            key = tut_slot_index.get((day, start_time))

        if key is None:
            raise ValueError(f"Invalid slot in 'Unwanted:' {day} {start_time}")
        
        unwanted_list.append({
            "event_id": event_id,
            "slot_key": key
        })

    return unwanted_list

# Parse preferences
# Return list of preferences
def parse_preferences(lines, events_by_id, lec_slot_index, tut_slot_index):

    pref_list = []

    for line in lines:
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        day, start_time, event_id, value_str = parts

        if event_id not in events_by_id:
            #raise ValueError(f"Unknown event in 'Preferences:' {event_id}")
            print(f"WARNING: Preference references unknown event: {event_id}, skipping line.")
            continue
        
        event_obj = events_by_id[event_id]
        value = int(value_str)

        if event_obj.kind == "LEC":
            key = lec_slot_index.get((day, start_time))
        else:
            key = tut_slot_index.get((day, start_time))

        if key is None:
            raise ValueError(f"Invalid slot in 'Preferences:' {day} {start_time}")

        pref_list.append({
            "event_id": event_id,
            "slot": key,
            "value": value
        })

    return pref_list

# Parse pair constraints
def parse_pair(lines, events_by_id):

    pairs_list = []

    for line in lines:
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        event_a_id, event_b_id = parts

        if event_a_id not in events_by_id:
            raise ValueError(f"Unknown event in Pair: {event_a_id}")
        if event_b_id not in events_by_id:
            raise ValueError(f"Unknown event in Pair: {event_b_id}")
        
        pairs_list.append({
            "event_a_id": event_a_id,
            "event_b_id": event_b_id
        })

    return pairs_list

# Parse partial assignments
def parse_partial_assignments(lines, events_by_id, lec_slot_index, tut_slot_index):

    partial_list = []

    for line in lines:
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        event_id, day, start_time = parts

        if event_id not in events_by_id:
            raise ValueError(f"Unknown event in 'Partial assignments:' {event_id}")
        
        event_obj = events_by_id[event_id]

        if event_obj.kind == "LEC":
            key = lec_slot_index.get((day, start_time))
        else:
            key = tut_slot_index.get((day, start_time))

        if key is None:
            raise ValueError(f"Invalid slot in 'Partial assignments:' {day} {start_time}")
        
        partial_list.append({
            "event_id": event_id,
            "slot": key
        })

    return partial_list

# Parses entire input file
# Returns ProblemInstance object
def parse_problem_instance(path):

    # Read all lines
    all_lines = read_all_lines(path)
    sections = split_into_sections(all_lines)

    # Parse events
    lec_by_id, course_list = parse_lectures(sections["Lectures:"])
    tut_by_id, tut_list = parse_tutorials(sections["Tutorials:"])

    # Merge into single 'events_by_id' dict
    events_by_id = {}
    events_by_id.update(lec_by_id)
    events_by_id.update(tut_by_id)

    # Parse slots
    lec_slots_by_key, lec_slot_index = parse_lecture_slots(sections["Lecture slots:"])
    tut_slots_by_key, tut_slot_index = parse_tutorial_slots(sections["Tutorial slots:"])

    # Parse constraints
    not_compatible_list = parse_not_compatible(
        sections["Not compatible:"],
        events_by_id
    )

    unwanted_list = parse_unwanted(
        sections["Unwanted:"],
        events_by_id,
        lec_slot_index,
        tut_slot_index
    )

    pref_list = parse_preferences(
        sections["Preferences:"],
        events_by_id,
        lec_slot_index,
        tut_slot_index
    )

    pair_list = parse_pair(
        sections["Pair:"],
        events_by_id
    )

    partial_assignments = parse_partial_assignments(
        sections["Partial assignments:"],
        events_by_id,
        lec_slot_index,
        tut_slot_index
    )

    # Problem name
    name_list = sections["Name:"]
    name = name_list[0] if name_list else "UnnamedProblem"

    # Build and return problem instance
    return ProblemInstance(
        name=name,

        # events
        lec_by_id=lec_by_id,
        tut_by_id=tut_by_id,
        events_by_id=events_by_id,
        course_list=course_list,
        tut_list=tut_list,

        # slots
        lec_slots_by_key=lec_slots_by_key,
        tut_slots_by_key=tut_slots_by_key,
        lec_slot_index=lec_slot_index,
        tut_slot_index=tut_slot_index,

        # constraints
        not_compatible=not_compatible_list,
        unwanted=unwanted_list,
        preferences=pref_list,
        pairs=pair_list,
        partial_assignments=partial_assignments
    )



       
