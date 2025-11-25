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
    
# Parse one lecture definition line
def parse_lecture_line(line: str) -> Event:

    # Split identifier from bool
    left, al_flag_text = line.split(",")
    al_required = parse_bool(al_flag_text)

    # Split up parts
    parts = left.strip().split()

    # Assign parts
    # The list looks like this for indexing:
    # [CPSC, 231, LEC, 01]
    program_code = parts[0]
    course_no = int(parts[1])
    kind = parts[2] # This should always be "LEC" but have this here anyways
    section_num = parts[3]
    section_label = f"{kind} {section_num}"

    # Evening condition
    is_evening_event = section_num.startswith("9")

    # 500 level condition
    is_500_course = (course_no >= 500)

    if (program_code == "CPSC") and course_no in (851, 913):
        is_special_tut = True
    else:
        is_special_tut = False

    event_id = f"{program_code} {course_no} {kind} {section_num}"

    # Construct event object
    return Event(
        id=event_id,
        kind=kind,
        program_code=program_code,
        course_no=course_no,
        section_label=section_label,
        tutorial_label=None,
        al_required=al_required,
        is_evening_event=is_evening_event,
        is_500_course=is_500_course,
        is_special_tut=is_special_tut,
    )

def parse_tutorial_line(line: str) -> Event:
    
    # Split identifier from bool
    left, al_flag_text = line.split(",")
    al_required = parse_bool(al_flag_text)

    # Split up parts
    parts = left.strip().split()

    # Assign parts
    program_code = parts[0]
    course_no = int(parts[1])

    # Special case - tutorial without lecture prefix
    # [SENG 300 TUT 01]
    if parts[2] in ("TUT", "LAB"):
        kind = parts[2]
        tut_num = parts[3]
        section_num = tut_num
        tutorial_label = f"{kind} {tut_num}"

        # This is a bit sketchy and needs clarification
        section_label = f"LEC {tut_num}"

        event_id = f"{program_code} {course_no} {tutorial_label}"

    # [CPSC, 231, LEC, 01, TUT, 01]
    else:

        lec_prefix = parts[2]
        section_num = parts[3]
        kind = parts[4]
        section_label = f"{kind} {section_num}"
        tut_num = parts[5]
        tutorial_label = f"{kind} {tut_num}"

        event_id = f"{program_code} {course_no} {lec_prefix} {section_num} {kind} {tut_num}"


    # Evening condition
    is_evening_event = section_num.startswith("9")

    # 500 level condition
    is_500_course = (course_no >= 500)

    if (program_code == "CPSC") and course_no in(851, 913):
        is_special_tut = True
    else:
        is_special_tut = False

    # Construct event object
    return Event(
        id=event_id,
        kind=kind,
        program_code=program_code,
        course_no=course_no,
        section_label=section_label,
        tutorial_label=tutorial_label,
        al_required=al_required,
        is_evening_event=is_evening_event,
        is_500_course=is_500_course,
        is_special_tut=is_special_tut,
    )


# Given lines under lecture return:
# lec_by_id
# course_list
def parse_lectures(lines):

    lec_by_id = {}
    course_list = {}

    for line in lines:
        event = parse_lecture_line(line)
        lec_by_id[event.id] = event

        key = (event.program_code, event.course_no)
        course_list.setdefault(key, []).append(event.id)

    return lec_by_id, course_list

# Given lines under tutorial return:
# tut_by_id
# tut_list
def parse_tutorials(lines):

    tut_by_id = {}
    tut_list = {}

    for line in lines:
        event = parse_tutorial_line(line)
        tut_by_id[event.id] = event

        key = (event.program_code, event.course_no)
        tut_list.setdefault(key, []).append(event.id)

    return tut_by_id, tut_list

# Parse all lecture slots and make:
# lec_slots_by_key
# lec_slot_index
def parse_lecture_slots(lines):
    lec_slots_by_key = {}
    lec_slot_index = {}

    forbidden_day = "TU"
    forbidden_start = time(11,0)
    forbidden_end = time(12, 30)

    for line in lines:

        # MO, 8:00, 3, 2, 0
        parts = [p.strip() for p in line.split(",")]

        day = parts[0]
        start_time = parts[1]

        hour, minute = map(int, start_time.split(":"))
        start_time_obj = time(hour, minute)

        lecture_max = int(parts[2])
        lecture_min = int(parts[3])
        al_lecture_max = int(parts[4])

        is_evening_slot = (hour >= 18)

        forbidden_for_lectures = (
            day == "TU" and 
            forbidden_start <= start_time_obj <= forbidden_end
        )

        slot_key = ("LEC", day, start_time)

        lec_slot_obj = LectureSlot(
            slot_key=slot_key,
            kind="LEC",
            day=day,
            start_time=start_time,
            is_evening_slot=is_evening_slot,
            lecture_max=lecture_max,
            lecture_min=lecture_min,
            al_lecture_max=al_lecture_max,
            forbidden_for_lectures=forbidden_for_lectures
        )

        lec_slots_by_key[slot_key] = lec_slot_obj
        lec_slot_index[(day, start_time)] = slot_key

    return lec_slots_by_key, lec_slot_index

# Parse all lecture slots and make:
# tut_slots_by_key
# tut_slot_index
def parse_tutorial_slots(lines):

    tut_slots_by_key = {}
    tut_slot_index = {}

    for line in lines:

        # MO, 8:00, 3, 2, 0
        parts = [p.strip() for p in line.split(",")]

        day = parts[0]
        start_time = parts[1]

        hour = int(start_time.split(":")[0])
        is_evening_slot = (hour >= 18)

        tutorial_max = int(parts[2])
        tutorial_min = int(parts[3])
        al_tutorial_max = int(parts[4])

        is_tth_18_19_tutorial = (day in ("TU", "TH") and start_time == "18:00")

        slot_key = ("TUT", day, start_time)

        tut_slot_obj = TutorialSlot(
            slot_key=slot_key,
            kind="TUT",
            day=day,
            start_time=start_time,
            is_evening_slot=is_evening_slot,
            tutorial_max=tutorial_max,
            tutorial_min=tutorial_min,
            al_tutorial_max=al_tutorial_max,
            is_tth_18_19_tutorial=is_tth_18_19_tutorial
        )

        tut_slots_by_key[slot_key] = tut_slot_obj
        tut_slot_index[(day, start_time)] = slot_key

    return tut_slots_by_key, tut_slot_index



       
