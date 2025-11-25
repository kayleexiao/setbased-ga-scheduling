# Slot class definitions and parsing functions for lecture and tutorial slots

from .utils import strip_and_split, is_evening_time
from .constants import (
    EVENT_KIND_LECTURE, EVENT_KIND_TUTORIAL,
    VALID_LECTURE_DAYS, VALID_TUTORIAL_DAYS,
    FORBIDDEN_LECTURE_DAY, FORBIDDEN_LECTURE_TIME,
    SPECIAL_TUTORIAL_DAY_TU, SPECIAL_TUTORIAL_TIME
)

# represents a lecture time slot
class LectureSlot:
    def __init__(self, day, start_time, lecture_max, lecture_min, al_lecture_max):
        if day not in VALID_LECTURE_DAYS:
            raise ValueError(f"Invalid lecture day: {day}. Must be one of {VALID_LECTURE_DAYS}")
        
        self.slot_key = (EVENT_KIND_LECTURE, day, start_time)
        self.kind = EVENT_KIND_LECTURE
        self.day = day
        self.start_time = start_time
        self.lecture_max = lecture_max
        self.lecture_min = lecture_min
        self.al_lecture_max = al_lecture_max
        self.is_evening_slot = is_evening_time(start_time)
        
        # check if this is the forbidden Tuesday 11:00-12:30 slot
        self.forbidden_for_lectures = (day == FORBIDDEN_LECTURE_DAY and start_time == FORBIDDEN_LECTURE_TIME)
    
    # representation of the lecture slot
    def __repr__(self):
        return f"LectureSlot(day='{self.day}', time='{self.start_time}', max={self.lecture_max})"
    
    # string representation of the lecture slot
    def __str__(self):
        return f"{self.day}, {self.start_time}"

# represents a tutorial/lab time slot
class TutorialSlot:
    def __init__(self, day, start_time, tutorial_max, tutorial_min, al_tutorial_max):
        if day not in VALID_TUTORIAL_DAYS:
            raise ValueError(f"Invalid tutorial day: {day}. Must be one of {VALID_TUTORIAL_DAYS}")
        
        self.slot_key = (EVENT_KIND_TUTORIAL, day, start_time)
        self.kind = EVENT_KIND_TUTORIAL
        self.day = day
        self.start_time = start_time
        self.tutorial_max = tutorial_max
        self.tutorial_min = tutorial_min
        self.al_tutorial_max = al_tutorial_max
        self.is_evening_slot = is_evening_time(start_time)
        
        # Check if this is the special Tu/Th 18:00-19:00 slot for CPSC 851/913
        self.is_tth_18_19_tutorial = (day == SPECIAL_TUTORIAL_DAY_TU and start_time == SPECIAL_TUTORIAL_TIME)
    
    # representation of the tutorial slot
    def __repr__(self):
        return f"TutorialSlot(day='{self.day}', time='{self.start_time}', max={self.tutorial_max})"
    
    # string representation of the tutorial slot
    def __str__(self):
        return f"{self.day}, {self.start_time}"

# parse lecture slots from lines
# return mapping of slot_key to LectureSlot object and index by (day, start_time)
# return mapping of (day, start_time) to slot_key
def parse_lecture_slots(lines):
    lec_slots_by_key = {}
    lec_slot_index = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 5:
            raise ValueError(f"Invalid lecture slot line format: {line}. Expected 5 fields.")
        
        day = parts[0].strip()
        start_time = parts[1].strip()
        lecture_max = int(parts[2].strip())
        lecture_min = int(parts[3].strip())
        al_lecture_max = int(parts[4].strip())
        
        # create LectureSlot object
        slot = LectureSlot(day, start_time, lecture_max, lecture_min, al_lecture_max)
        
        # add to dictionaries
        lec_slots_by_key[slot.slot_key] = slot
        lec_slot_index[(day, start_time)] = slot.slot_key
    
    return lec_slots_by_key, lec_slot_index

# parse tutorial slots from lines
# return mapping of slot_key to TutorialSlot object and index by (day, start_time)
# return mapping of (day, start_time) to slot_key
def parse_tutorial_slots(lines):
    tut_slots_by_key = {}
    tut_slot_index = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 5:
            raise ValueError(f"Invalid tutorial slot line format: {line}. Expected 5 fields.")
        
        day = parts[0].strip()
        start_time = parts[1].strip()
        tutorial_max = int(parts[2].strip())
        tutorial_min = int(parts[3].strip())
        al_tutorial_max = int(parts[4].strip())
        
        # create TutorialSlot object
        slot = TutorialSlot(day, start_time, tutorial_max, tutorial_min, al_tutorial_max)
        
        # add to dictionaries
        tut_slots_by_key[slot.slot_key] = slot
        tut_slot_index[(day, start_time)] = slot.slot_key
    
    return tut_slots_by_key, tut_slot_index