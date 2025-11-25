from dataclasses import dataclass
from typing import Dict
from .event import Event
from ..parser.slot import Slot

@dataclass
class Schedule:
    assignments: Dict[Event, Slot]