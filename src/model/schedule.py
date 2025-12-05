# Schedule class representing a complete assignment of events to slots.

# represents a schedule mapping events to their assigned slots
class Schedule:
    # initialize the schedule
    # e.g., sch = Schedule(assignments={event: lec_slot})
    def __init__(self, assignments=None):
        self.assignments = assignments if assignments is not None else {}
    
    # assign an event to a slot
    def assign(self, event, slot):
        self.assignments[event] = slot
    
    # getter func that returns the slot assigned to an event
    def get_assignment(self, event):
        return self.assignments.get(event)
    
    # check if an event is assigned to a slot
    def is_assigned(self, event):
        return event in self.assignments
    
    # returns a copy of the schedule
    def copy(self):
        return Schedule(assignments=dict(self.assignments))
    
    # count number of assignments in the schedule
    def count_assignments(self):
        return len(self.assignments)
    
    # representation of the schedule
    def __repr__(self):
        if not self.assignments:
            return "Schedule(empty)"
        
        lines = ["Schedule:"]
        for event, slot in self.assignments.items():
            lines.append(f"  {event.id} -> {slot}")
        return "\n".join(lines)
    
    # string representation of the schedule
    def __str__(self):
        return self.__repr__()