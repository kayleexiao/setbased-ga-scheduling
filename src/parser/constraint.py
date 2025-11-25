# Constraint class definitions and parsing functions.

from .helpers import strip_and_split, normalize_event_id

# represents a constraint that two events cannot be scheduled at overlapping times
class NotCompatible:
    def __init__(self, event_a_id, event_b_id):
        self.event_a_id = event_a_id
        self.event_b_id = event_b_id
    
    def __repr__(self):
        return f"NotCompatible('{self.event_a_id}', '{self.event_b_id}')"

# represents a constraint that an event should not be scheduled in a specific slot
class Unwanted:
    def __init__(self, event_id, slot_key):
        self.event_id = event_id
        self.slot_key = slot_key
    
    def __repr__(self):
        return f"Unwanted(event='{self.event_id}', slot={self.slot_key})"

# represents a soft constraint preference for scheduling an event in a specific slot
class Preference:
    def __init__(self, event_id, slot_key, value):
        self.event_id = event_id
        self.slot_key = slot_key
        self.value = value
    
    def __repr__(self):
        return f"Preference(event='{self.event_id}', slot={self.slot_key}, value={self.value})"

# represents a soft constraint that two events should be scheduled at the same time
class Pair:
    def __init__(self, event_a_id, event_b_id):
        self.event_a_id = event_a_id
        self.event_b_id = event_b_id
    
    def __repr__(self):
        return f"Pair('{self.event_a_id}', '{self.event_b_id}')"

# represents a fixed assignment of an event to a specific slot
class PartialAssignment:
    def __init__(self, event_id, slot_key):
        self.event_id = event_id
        self.slot_key = slot_key
    
    def __repr__(self):
        return f"PartialAssignment(event='{self.event_id}', slot={self.slot_key})"

# function to parse not compatible constraints from lines
# returns a list of NotCompatible objects
def parse_not_compatible(lines, events_by_id):
    not_compatible_list = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 2:
            raise ValueError(f"Invalid not compatible line format: {line}")
        
        event_a_id = normalize_event_id(parts[0])
        event_b_id = normalize_event_id(parts[1])
        
        # check if both events exist
        if event_a_id not in events_by_id:
            raise ValueError(f"Unknown event in not compatible: {event_a_id}")
        if event_b_id not in events_by_id:
            raise ValueError(f"Unknown event in not compatible: {event_b_id}")
        
        not_compatible_list.append(NotCompatible(event_a_id, event_b_id))
    
    return not_compatible_list

# function to parse unwanted constraints from lines
# returns a list of Unwanted objects
def parse_unwanted(lines, events_by_id, lec_slot_index, tut_slot_index):
    unwanted_list = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 3:
            raise ValueError(f"Invalid unwanted line format: {line}")
        
        event_id = normalize_event_id(parts[0])
        day = parts[1].strip()
        start_time = parts[2].strip()
        
        # check if event exists
        if event_id not in events_by_id:
            raise ValueError(f"Unknown event in unwanted: {event_id}")
        
        event = events_by_id[event_id]
        
        # check if event is a lecture or tutorial and get slot_key for it
        try:
            if event.is_lecture():
                slot_key = lec_slot_index[(day, start_time)]
            else:
                slot_key = tut_slot_index[(day, start_time)]
        except KeyError:
            raise ValueError(f"Unknown slot ({day}, {start_time}) for event {event_id}")
        
        unwanted_list.append(Unwanted(event_id, slot_key))
    
    return unwanted_list

# function to parse preference constraints from lines
# returns a list of Preference objects
def parse_preferences(lines, events_by_id, lec_slot_index, tut_slot_index):
    pref_list = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 4:
            raise ValueError(f"Invalid preference line format: {line}")
        
        day = parts[0].strip()
        start_time = parts[1].strip()
        event_id = normalize_event_id(parts[2])
        value = int(parts[3].strip())
        
        # check if event exists
        if event_id not in events_by_id:
            print(f"Warning: Unknown event in preferences: {event_id}. Skipping.")
            continue
        
        event = events_by_id[event_id]
        
        # check if event is a lecture or tutorial and get slot_key for it
        try:
            if event.is_lecture():
                slot_key = lec_slot_index[(day, start_time)]
            else:
                slot_key = tut_slot_index[(day, start_time)]
        except KeyError:
            print(f"Warning: Unknown slot ({day}, {start_time}) for event {event_id}. Skipping.")
            continue
        
        pref_list.append(Preference(event_id, slot_key, value))
    
    return pref_list

# function to parse pair constraints from lines
# returns a list of Pair objects
def parse_pair(lines, events_by_id):
    pair_list = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 2:
            raise ValueError(f"Invalid pair line format: {line}")
        
        event_a_id = normalize_event_id(parts[0])
        event_b_id = normalize_event_id(parts[1])
        
        # check if both events exist
        if event_a_id not in events_by_id:
            raise ValueError(f"Unknown event in pair: {event_a_id}")
        if event_b_id not in events_by_id:
            raise ValueError(f"Unknown event in pair: {event_b_id}")
        
        pair_list.append(Pair(event_a_id, event_b_id))
    
    return pair_list

# function to parse partial assignments from lines
# returns a list of PartialAssignment objects
def parse_partial_assignments(lines, events_by_id, lec_slot_index, tut_slot_index):
    partial_list = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = strip_and_split(line, ',')
        if len(parts) != 3:
            raise ValueError(f"Invalid partial assignment line format: {line}")
        
        event_id = normalize_event_id(parts[0])
        day = parts[1].strip()
        start_time = parts[2].strip()
        
        # check if event exists
        if event_id not in events_by_id:
            raise ValueError(f"Unknown event in partial assignment: {event_id}")
        
        event = events_by_id[event_id]
        
        # check if event is a lecture or tutorial and get slot_key for it
        try:
            if event.is_lecture():
                slot_key = lec_slot_index[(day, start_time)]
            else:
                slot_key = tut_slot_index[(day, start_time)]
        except KeyError:
            raise ValueError(f"Invalid slot ({day}, {start_time}) for event {event_id} in partial assignment")
        
        partial_list.append(PartialAssignment(event_id, slot_key))
    
    return partial_list