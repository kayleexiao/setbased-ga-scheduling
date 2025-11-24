from src.model.event import Event

# test event
event = Event(
    id="CPSC 231 LEC 01",
    kind="LEC",
    program_code="CPSC",
    course_no=231,
    section_label="LEC 01",
    tutorial_label=None,
    al_required=True,
    is_evening_event=False,
    is_500_course=False,
    is_special_tut=False
)

print(event)