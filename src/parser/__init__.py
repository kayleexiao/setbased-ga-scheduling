# package handles parsing and creating a structured problem instance

from .constants import *
from .helpers import *
from .event import Event
from .slot import LectureSlot, TutorialSlot
from .constraint import (
    NotCompatible, Unwanted, Preference, Pair, PartialAssignment
)
from .problem_instance import ProblemInstance

__all__ = [
    # constants
    'VALID_LECTURE_DAYS', 'VALID_TUTORIAL_DAYS',
    'EVENT_KIND_LECTURE', 'EVENT_KIND_TUTORIAL', 'EVENT_KIND_LAB',
    'TUTORIAL_TYPES', 'SECTION_HEADERS',
    
    # helpers
    'strip_and_split', 'parse_time', 'is_evening_time', 'parse_boolean',
    'is_empty_line', 'normalize_event_id',
    
    # classes
    'Event',
    'LectureSlot', 'TutorialSlot',
    'NotCompatible', 'Unwanted', 'Preference', 'Pair', 'PartialAssignment',
    'ProblemInstance',
]