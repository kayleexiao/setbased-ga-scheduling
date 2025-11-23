from dataclasses import dataclass
from .slot import Slot

@dataclass
class TutorialSlot(Slot):
    tutorial_max: int
    tutorial_min: int
    al_tutorial_max: int
    is_tth_18_19_tutorial: bool