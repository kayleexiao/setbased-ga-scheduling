# package handles parsing and creating a structured problem instance

from .constants import *
from .utils import *
from .event import Event, parse_lectures, parse_tutorials
from .slot import LectureSlot, TutorialSlot, parse_lecture_slots, parse_tutorial_slots
from .constraint import (
    NotCompatible, Unwanted, Preference, Pair, PartialAssignment,
    parse_not_compatible, parse_unwanted, parse_preferences,
    parse_pair, parse_partial_assignments
)
from .problem_instance import ProblemInstance

__all__ = [
    # constants
    'VALID_LECTURE_DAYS', 'VALID_TUTORIAL_DAYS',
    'EVENT_KIND_LECTURE', 'EVENT_KIND_TUTORIAL', 'EVENT_KIND_LAB',
    'TUTORIAL_TYPES', 'SECTION_HEADERS',
    
    # utils
    'strip_and_split', 'parse_time', 'is_evening_time', 'parse_boolean',
    'is_empty_line', 'normalize_event_id',
    
    # event classes and functions
    'Event', 'parse_lectures', 'parse_tutorials',
    
    # slot classes and functions
    'LectureSlot', 'TutorialSlot', 'parse_lecture_slots', 'parse_tutorial_slots',
    
    # constraint classes and functions
    'NotCompatible', 'Unwanted', 'Preference', 'Pair', 'PartialAssignment',
    'parse_not_compatible', 'parse_unwanted', 'parse_preferences',
    'parse_pair', 'parse_partial_assignments',
    
    # problem instance
    'ProblemInstance',
]