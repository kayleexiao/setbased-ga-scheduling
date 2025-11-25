from dataclasses import dataclass

@dataclass
class Slot:
    slot_key: tuple
    kind: str
    day: str
    start_time: str
    is_evening_slot: bool
