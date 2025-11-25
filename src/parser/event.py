# Event class definition and parsing functions for lectures and tutorials

from .helpers import strip_and_split, parse_boolean, normalize_event_id
from .constants import (
    EVENT_KIND_LECTURE, TUTORIAL_TYPES, EVENING_LECTURE_PREFIX,
    COURSE_500_LEVEL, SPECIAL_COURSE_851, SPECIAL_COURSE_913
)

# represents a lecture or tutorial event that needs to be scheduled.
# identifier: String like "CPSC 231 LEC 01" or "CPSC 231 LEC 01 TUT 01"
# al_required: Boolean indicating if active learning room is required
class Event:
    def __init__(self, identifier, al_required):
        self.id = normalize_event_id(identifier)
        self.al_required = al_required
        
        # parse the identifier
        parts = self.id.split()
        
        if len(parts) < 4:
            raise ValueError(f"Invalid event identifier: {identifier}")
        
        self.program_code = parts[0]  # e.g., "CPSC"
        self.course_no = int(parts[1])  # e.g., 231
        
        # determine if this is a lecture or tutorial
        if len(parts) == 4:
            # could be a lecture: "CPSC 231 LEC 01"
            # OR a tutorial without LEC prefix: "SENG 300 TUT 01"
            event_type = parts[2].upper()
            
            if event_type == "LEC":
                # this is a lecture
                self.kind = EVENT_KIND_LECTURE
                self.section_label = f"{parts[2]} {parts[3]}"  # "LEC 01"
                self.tutorial_label = None
            elif event_type in TUTORIAL_TYPES:
                # this is a tutorial/lab without LEC prefix: "SENG 300 TUT 01"
                self.kind = event_type  # TUT or LAB
                self.section_label = None  # no lecture section for standalone tutorials
                self.tutorial_label = f"{parts[2]} {parts[3]}"  # "TUT 01" or "LAB 01"
            else:
                raise ValueError(f"Unknown event type: {parts[2]}. Expected LEC, TUT, or LAB.")
        elif len(parts) == 6:
            # this is a tutorial: "CPSC 231 LEC 01 TUT 01" or "CPSC 231 LEC 01 LAB 01"
            self.section_label = f"{parts[2]} {parts[3]}"  # "LEC 01"
            
            # check if it's TUT or LAB (but both treated as tutorials)
            tut_kind = parts[4].upper()
            if tut_kind in TUTORIAL_TYPES:
                self.kind = tut_kind  # store actual kind (TUT or LAB)
            else:
                raise ValueError(f"Unknown tutorial kind: {tut_kind}. Expected TUT or LAB.")
            
            self.tutorial_label = f"{parts[4]} {parts[5]}"  # "TUT 01" or "LAB 01"
        else:
            raise ValueError(f"Invalid event identifier format: {identifier}")
        
        # check if this is an evening event (LEC 9X prefix)
        self.is_evening_event = self.section_label and self.section_label.startswith(EVENING_LECTURE_PREFIX) or False
        
        # check if this is a 500-level course
        self.is_500_course = self.course_no >= COURSE_500_LEVEL
        
        # check if this is a special tutorial (CPSC 851 or CPSC 913)
        course_key = f"{self.program_code} {self.course_no}"
        self.is_special_tut = course_key in [SPECIAL_COURSE_851, SPECIAL_COURSE_913]
    
    # check if event is lecture
    def is_lecture(self):
        return self.kind == EVENT_KIND_LECTURE
    
    # check if event is tutorial/lab
    def is_tutorial(self):
        return self.kind in TUTORIAL_TYPES
    
    # get course identifier (program_code, course_no) tuple
    def get_course_key(self):
        return (self.program_code, self.course_no)
    
    # representation of the event
    def __repr__(self):
        return f"Event(id='{self.id}', kind='{self.kind}', al_required={self.al_required})"
    
    # string representation of the event ID
    def __str__(self):
        return self.id

# parse lectures from lines
# return mapping of lecture IDs to Event objects
# return mapping of (program_code, course_no) to list of lecture IDs
def parse_lectures(lines):
    lec_by_id = {}
    course_list = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 2:
            raise ValueError(f"Invalid lecture line format: {line}")
        
        identifier = parts[0].strip()
        al_required = parse_boolean(parts[1])
        
        # create Event object
        event = Event(identifier, al_required)
        
        if not event.is_lecture():
            raise ValueError(f"Expected lecture but got tutorial: {identifier}")
        
        # add to lec_by_id
        lec_by_id[event.id] = event
        
        # add to course_list
        course_key = event.get_course_key()
        if course_key not in course_list:
            course_list[course_key] = []
        course_list[course_key].append(event.id)
    
    return lec_by_id, course_list

# parse tutorials from lines
# return mapping of tutorial IDs to Event objects
# return mapping of (program_code, course_no) to list of tutorial IDs
def parse_tutorials(lines):
    tut_by_id = {}
    tut_list = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 2:
            raise ValueError(f"Invalid tutorial line format: {line}")
        
        identifier = parts[0].strip()
        al_required = parse_boolean(parts[1])
        
        # Create Event object
        event = Event(identifier, al_required)
        
        if not event.is_tutorial():
            raise ValueError(f"Expected tutorial/lab but got lecture: {identifier}")
        
        # Add to tut_by_id
        tut_by_id[event.id] = event
        
        # Add to tut_list
        course_key = event.get_course_key()
        if course_key not in tut_list:
            tut_list[course_key] = []
        tut_list[course_key].append(event.id)
    
    return tut_by_id, tut_list