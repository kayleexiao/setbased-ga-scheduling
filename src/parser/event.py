from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    id: str
    kind: str
    program_code: str
    course_no: int
    section_label: str
    tutorial_label: str | None
    al_required: bool
    is_evening_event: bool
    is_500_course: bool
    is_special_tut: bool
    