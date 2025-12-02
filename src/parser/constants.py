# constants used throughout the parser

# valid days for slots
VALID_LECTURE_DAYS = {"MO", "TU"}
VALID_TUTORIAL_DAYS = {"MO", "TU", "FR"}

# event kinds
EVENT_KIND_LECTURE = "LEC"
EVENT_KIND_TUTORIAL = "TUT"
EVENT_KIND_LAB = "LAB"

# tutorial types (both TUT and LAB are treated as tutorials)
TUTORIAL_TYPES = {EVENT_KIND_TUTORIAL, EVENT_KIND_LAB}

# section headers in input file
SECTION_NAME = "Name:"
SECTION_LECTURE_SLOTS = "Lecture slots:"
SECTION_TUTORIAL_SLOTS = "Tutorial slots:"
SECTION_LECTURES = "Lectures:"
SECTION_TUTORIALS = "Tutorials:"
SECTION_NOT_COMPATIBLE = "Not compatible:"
SECTION_UNWANTED = "Unwanted:"
SECTION_PREFERENCES = "Preferences:"
SECTION_PAIR = "Pair:"
SECTION_PARTIAL_ASSIGNMENTS = "Partial assignments:"

# all section headers in order
SECTION_HEADERS = [
    SECTION_NAME,
    SECTION_LECTURE_SLOTS,
    SECTION_TUTORIAL_SLOTS,
    SECTION_LECTURES,
    SECTION_TUTORIALS,
    SECTION_NOT_COMPATIBLE,
    SECTION_UNWANTED,
    SECTION_PREFERENCES,
    SECTION_PAIR,
    SECTION_PARTIAL_ASSIGNMENTS
]

# evening slot threshold (18:00 or later)
EVENING_HOUR_THRESHOLD = 18

# special tutorial slots
SPECIAL_TUTORIAL_TIME = "18:00"
SPECIAL_TUTORIAL_DAY_TU = "TU"

# special courses
SPECIAL_COURSE_851 = "CPSC 851"
SPECIAL_COURSE_913 = "CPSC 913"
RELATED_COURSE_351 = "CPSC 351" # related to CPSC 851 (cannot overlap)
RELATED_COURSE_413 = "CPSC 413" # related to CPSC 913 (cannot overlap)

# Tuesday department meeting slot (11:00-12:30)
FORBIDDEN_LECTURE_DAY = "TU"
FORBIDDEN_LECTURE_TIME = "11:00"

# evening lecture prefix
EVENING_LECTURE_PREFIX = "LEC 9"

# 500-level course threshold
COURSE_500_LEVEL = 500