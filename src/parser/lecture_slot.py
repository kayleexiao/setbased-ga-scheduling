from dataclasses import dataclass
from ..parser.slot import Slot

@dataclass
class LectureSlot(Slot):
    lecture_max: int
    lecture_min: int
    al_lecture_max: int
    forbidden_for_lectures: bool