# Main parser module for reading and parsing the input file

from .constants import SECTION_HEADERS
from .helpers import is_empty_line
from .event import Event, parse_lectures, parse_tutorials
from .slot import parse_lecture_slots, parse_tutorial_slots
from .constraint import (
    NotCompatible,
    parse_not_compatible, parse_unwanted, parse_preferences,
    parse_pair, parse_partial_assignments
)
from .problem_instance import ProblemInstance

# function to read all lines from the input file
# returns a list of strings (lines)
def read_all_lines(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    except Exception as e:
        raise Exception(f"Error reading file {filepath}: {e}")

# function to split lines into sections based on headers
# returns a dictionary mapping section header to list of lines in that section
def split_into_sections(all_lines):
    sections = {
        "Name:": [],
        "Lecture slots:": [],
        "Tutorial slots:": [],
        "Lectures:": [],
        "Tutorials:": [],
        "Not compatible:": [],
        "Unwanted:": [],
        "Preferences:": [],
        "Pair:": [],
        "Partial assignments:": []
    }
    
    current_section = None
    
    for line in all_lines:
        # check if this line is a section header
        stripped = line.strip()
        
        if stripped in sections.keys():
            current_section = stripped
        elif current_section is not None and not is_empty_line(line):
            # add non-empty lines to the current section (stripped)
            sections[current_section].append(stripped)
    
    return sections

# main function to parse the entire input file and create a ProblemInstance
# returns a ProblemInstance object
def parse_input_file(filepath, pen_lecturemin=1, pen_tutorialmin=1,
                     pen_notpaired=1, pen_section=1,
                     w_minfilled=1, w_pref=1, w_pair=1, w_secdiff=1):
    # step 1: read all lines from file
    all_lines = read_all_lines(filepath)
    
    # step 2: split into sections
    sections = split_into_sections(all_lines)
    
    # step 3: create problem instance
    problem = ProblemInstance()
    
    # parse name
    if sections["Name:"]:
        problem.name = sections["Name:"][0].strip()
    else:
        problem.name = "Unnamed Problem"
    
    # step 4: parse slots first (needed for other parsing)
    print("Parsing lecture slots...")
    problem.lec_slots_by_key, problem.lec_slot_index = parse_lecture_slots(
        sections["Lecture slots:"]
    )
    
    print("Parsing tutorial slots...")
    problem.tut_slots_by_key, problem.tut_slot_index = parse_tutorial_slots(
        sections["Tutorial slots:"]
    )
    
    # step 5: parse events
    print("Parsing lectures...")
    problem.lec_by_id, problem.course_list = parse_lectures(
        sections["Lectures:"]
    )
    
    print("Parsing tutorials...")
    problem.tut_by_id, problem.tut_list = parse_tutorials(
        sections["Tutorials:"]
    )
    
    # merge lecture and tutorial dictionaries into events_by_id
    problem.events_by_id = {**problem.lec_by_id, **problem.tut_by_id}
    
    # step 6: handle special courses (CPSC 851 and 913)
    handle_special_courses(problem)
    
    # step 7: parse constraints
    print("Parsing constraints...")
    
    problem.not_compatible = parse_not_compatible(
        sections["Not compatible:"],
        problem.events_by_id
    )
    
    problem.unwanted = parse_unwanted(
        sections["Unwanted:"],
        problem.events_by_id,
        problem.lec_slot_index,
        problem.tut_slot_index
    )
    
    problem.preferences = parse_preferences(
        sections["Preferences:"],
        problem.events_by_id,
        problem.lec_slot_index,
        problem.tut_slot_index
    )
    
    problem.pairs = parse_pair(
        sections["Pair:"],
        problem.events_by_id
    )
    
    problem.partial_assignments = parse_partial_assignments(
        sections["Partial assignments:"],
        problem.events_by_id,
        problem.lec_slot_index,
        problem.tut_slot_index
    )
    
    # step 8: set penalties and weights
    problem.set_penalties(pen_lecturemin, pen_tutorialmin, pen_notpaired, pen_section)
    problem.set_weights(w_minfilled, w_pref, w_pair, w_secdiff)
    
    # step 9: validate partial assignments
    validate_partial_assignments(problem)
    
    print(f"Parsing complete: {problem}")
    return problem

# function to handle special courses CPSC 851 and CPSC 913
    # - if CPSC 351 lectures exist, CPSC 851 tut must be scheduled
    # - if CPSC 413 lectures exist, CPSC 913 tut must be scheduled
    # - scheduled in tutorial slots at Tu/Th 18:00-19:00
def handle_special_courses(problem):
    from .event import Event
    from .constraint import NotCompatible
    
    # check if CPSC 351 exists
    cpsc_351_lectures = problem.get_lectures_for_course("CPSC", 351)
    if cpsc_351_lectures:
        # create CPSC 851 if it doesn't exist
        cpsc_851_id = "CPSC 851 TUT 01"
        if cpsc_851_id not in problem.events_by_id:
            print(f"Adding special course: {cpsc_851_id}")
            event_851 = Event(cpsc_851_id, al_required=False)
            event_851.is_special_tut = True
            problem.tut_by_id[cpsc_851_id] = event_851
            problem.events_by_id[cpsc_851_id] = event_851
            
            # add to tut_list
            course_key = (event_851.program_code, event_851.course_no)
            if course_key not in problem.tut_list:
                problem.tut_list[course_key] = []
            problem.tut_list[course_key].append(cpsc_851_id)
        
        # add not compatible constraints between CPSC 851 and all CPSC 351 sections
        for cpsc_351_id in cpsc_351_lectures:
            problem.not_compatible.append(NotCompatible(cpsc_851_id, cpsc_351_id))
        
        # also add not compatible for CPSC 351 tutorials
        cpsc_351_tutorials = problem.get_tutorials_for_course("CPSC", 351)
        for cpsc_351_tut_id in cpsc_351_tutorials:
            problem.not_compatible.append(NotCompatible(cpsc_851_id, cpsc_351_tut_id))
    
    # check if CPSC 413 exists
    cpsc_413_lectures = problem.get_lectures_for_course("CPSC", 413)
    if cpsc_413_lectures:
        # create CPSC 913 if it doesn't exist
        cpsc_913_id = "CPSC 913 TUT 01"
        if cpsc_913_id not in problem.events_by_id:
            print(f"Adding special course: {cpsc_913_id}")
            event_913 = Event(cpsc_913_id, al_required=False)
            event_913.is_special_tut = True
            problem.tut_by_id[cpsc_913_id] = event_913
            problem.events_by_id[cpsc_913_id] = event_913
            
            # add to tut_list
            course_key = (event_913.program_code, event_913.course_no)
            if course_key not in problem.tut_list:
                problem.tut_list[course_key] = []
            problem.tut_list[course_key].append(cpsc_913_id)
        
        # add not compatible constraints between CPSC 913 and all CPSC 413 sections
        for cpsc_413_id in cpsc_413_lectures:
            problem.not_compatible.append(NotCompatible(cpsc_913_id, cpsc_413_id))
        
        # also add not compatible for CPSC 413 tutorials
        cpsc_413_tutorials = problem.get_tutorials_for_course("CPSC", 413)
        for cpsc_413_tut_id in cpsc_413_tutorials:
            problem.not_compatible.append(NotCompatible(cpsc_913_id, cpsc_413_tut_id))

# function to validate partial assignments are satisfiable
# i.e., lecture assigned to lecture slot, tutorial to tutorial slot
def validate_partial_assignments(problem):
    for pa in problem.partial_assignments:
        event = problem.get_event(pa.event_id)
        slot = problem.get_slot(pa.slot_key)
        
        if event is None:
            raise ValueError(f"Partial assignment references unknown event: {pa.event_id}")
        
        if slot is None:
            raise ValueError(f"Partial assignment references unknown slot: {pa.slot_key}")
        
        # check that lecture is assigned to lecture slot
        if event.is_lecture() and slot.kind != "LEC":
            raise ValueError(
                f"Partial assignment error: Lecture {pa.event_id} assigned to tutorial slot {pa.slot_key}"
            )
        
        # check that tutorial is assigned to tutorial slot
        if event.is_tutorial() and slot.kind != "TUT":
            raise ValueError(
                f"Partial assignment error: Tutorial {pa.event_id} assigned to lecture slot {pa.slot_key}"
            )
            
    print(f"Validated {len(problem.partial_assignments)} partial assignments")

# function to parse preference constraints from lines
# returns a list of Preference objects
def parse_from_command_line(args):
    """
    Expected format:
    python main.py <input_file> <w_minfilled> <w_pref> <w_pair> <w_secdiff>
                   <pen_lecturemin> <pen_tutorialmin> <pen_notpaired> <pen_section>
    """
    if len(args) < 9:
        raise ValueError(
            "Usage: <input_file> <w_minfilled> <w_pref> <w_pair> <w_secdiff> "
            "<pen_lecturemin> <pen_tutorialmin> <pen_notpaired> <pen_section>"
        )
    
    filepath = args[0]
    w_minfilled = int(args[1])
    w_pref = int(args[2])
    w_pair = int(args[3])
    w_secdiff = int(args[4])
    pen_lecturemin = int(args[5])
    pen_tutorialmin = int(args[6])
    pen_notpaired = int(args[7])
    pen_section = int(args[8])
    
    return parse_input_file(
        filepath,
        pen_lecturemin=pen_lecturemin,
        pen_tutorialmin=pen_tutorialmin,
        pen_notpaired=pen_notpaired,
        pen_section=pen_section,
        w_minfilled=w_minfilled,
        w_pref=w_pref,
        w_pair=w_pair,
        w_secdiff=w_secdiff
    )