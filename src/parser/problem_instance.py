from dataclasses import dataclass

@dataclass
class ProblemInstance:
    # meta
    name: str

    # events
    lec_by_id: dict
    tut_by_id: dict
    events_by_id: dict
    course_list: dict
    tut_list: dict

    # slots
    lec_slots_by_key: dict   
    tut_slots_by_key: dict    
    lec_slot_index: dict       
    tut_slot_index: dict    

    # constraints
    not_compatible: list      
    unwanted: list             
    preferences: list          
    pairs: list               
    partial_assignments: list    
