import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.constants import TUTORIAL_TYPES, EVENT_KIND_TUTORIAL, EVENT_KIND_LAB
from parser.event import Event

print("TUTORIAL_TYPES:", TUTORIAL_TYPES)
print("EVENT_KIND_TUTORIAL:", EVENT_KIND_TUTORIAL)
print("EVENT_KIND_LAB:", EVENT_KIND_LAB)
print()

# Test parsing SENG 300 TUT 01
print("Testing: SENG 300 TUT 01")
try:
    event = Event("SENG 300 TUT 01", al_required=False)
    print(f"Success! Created event: {event}")
    print(f"  - kind: {event.kind}")
    print(f"  - is_tutorial(): {event.is_tutorial()}")
    print(f"  - is_lecture(): {event.is_lecture()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()