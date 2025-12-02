# problem instance that holds all parsed data
class ProblemInstance:
    def __init__(self):
        # meta
        self.name = None
        
        # events
        self.lec_by_id = {}          # dict: lecture_id -> Event
        self.tut_by_id = {}          # dict: tutorial_id -> Event
        self.events_by_id = {}       # dict: event_id -> Event (all events)
        self.course_list = {}        # dict: (program_code, course_no) -> [lecture_ids]
        self.tut_list = {}           # dict: (program_code, course_no) -> [tutorial_ids]
        
        # slots
        self.lec_slots_by_key = {}   # dict: slot_key -> LectureSlot
        self.tut_slots_by_key = {}   # dict: slot_key -> TutorialSlot
        self.lec_slot_index = {}     # dict: (day, start_time) -> slot_key
        self.tut_slot_index = {}     # dict: (day, start_time) -> slot_key
        
        # constraints
        self.not_compatible = []     # list of NotCompatible
        self.unwanted = []           # list of Unwanted
        self.preferences = []        # list of Preference
        self.pairs = []              # list of Pair
        self.partial_assignments = [] # list of PartialAssignment
        
        # penalty values (from command line)
        self.pen_lecturemin = 0
        self.pen_tutorialmin = 0
        self.pen_notpaired = 0
        self.pen_section = 0
        
        # weight values (from command line)
        self.w_minfilled = 0
        self.w_pref = 0
        self.w_pair = 0
        self.w_secdiff = 0
    
    # func to set penalties from command line
    def set_penalties(self, pen_lecturemin, pen_tutorialmin, pen_notpaired, pen_section):
        self.pen_lecturemin = pen_lecturemin # penalty for not meeting minimum lecture count
        self.pen_tutorialmin = pen_tutorialmin # penalty for not meeting minimum tutorial count
        self.pen_notpaired = pen_notpaired # penalty for not pairing events that should be paired
        self.pen_section = pen_section # penalty for scheduling same course sections at same time
    
    # func to set weights from command line
    def set_weights(self, w_minfilled, w_pref, w_pair, w_secdiff):
        self.w_minfilled = w_minfilled # weight for minimum filled constraint
        self.w_pref = w_pref # weight for preference constraint
        self.w_pair = w_pair # weight for pair constraint
        self.w_secdiff = w_secdiff # weight for section difference constraint
    
    # getter func for list of lecture IDs
    def get_all_lecture_ids(self):
        return list(self.lec_by_id.keys())
    
    # getter func for list of tutorial IDs
    def get_all_tutorial_ids(self):
        return list(self.tut_by_id.keys())
    
    # getter func for list of all event IDs (lec + tut)
    def get_all_event_ids(self):
        return list(self.events_by_id.keys())
    
    # getter func for list of lecture IDs for a specific course
    def get_lectures_for_course(self, program_code, course_no):
        return self.course_list.get((program_code, course_no), [])
    
    # getter func for list of tutorial IDs for a specific course
    def get_tutorials_for_course(self, program_code, course_no):
        return self.tut_list.get((program_code, course_no), [])
    
    # getter func for an event by its ID (e.g. "CPSC 231 LEC 01"), returns Event object or None
    def get_event(self, event_id):
        return self.events_by_id.get(event_id)
    
    # getter func for a lecture slot by its key (tuple (kind, day, start_time))
    # returns LectureSlot object or None
    def get_lecture_slot(self, slot_key):
        return self.lec_slots_by_key.get(slot_key)
    
    # getter func for a tutorial slot by its key (tuple (kind, day, start_time))
    # returns TutorialSlot object or None
    def get_tutorial_slot(self, slot_key):
        return self.tut_slots_by_key.get(slot_key)
    
    # getter func for a slot (lecture or tutorial) by its key (tuple (kind, day, start_time))
    # returns Slot object or None
    def get_slot(self, slot_key):
        if slot_key in self.lec_slots_by_key:
            return self.lec_slots_by_key[slot_key]
        return self.tut_slots_by_key.get(slot_key)
    
    # getter func for all lecture slot keys
    # returns list of slot_keys
    def get_all_lecture_slot_keys(self):
        """Returns list of all lecture slot_keys"""
        return list(self.lec_slots_by_key.keys())
    
    # getter func for all tutorial slot keys
    # returns list of slot_keys
    def get_all_tutorial_slot_keys(self):
        """Returns list of all tutorial slot_keys"""
        return list(self.tut_slots_by_key.keys())
    
    # string representation of the ProblemInstance object
    def __repr__(self):
        return (f"ProblemInstance(name='{self.name}', "
                f"lectures={len(self.lec_by_id)}, "
                f"tutorials={len(self.tut_by_id)}, "
                f"lec_slots={len(self.lec_slots_by_key)}, "
                f"tut_slots={len(self.tut_slots_by_key)})")