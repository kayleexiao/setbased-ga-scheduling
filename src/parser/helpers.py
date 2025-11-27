# some helper functions for parsing

# function to strip whitespace and split a line by a delimiter
# returns a list of stripped parts
def strip_and_split(line, delimiter=','):
    return [part.strip() for part in line.split(delimiter)]

# function to parse time in HH:MM format and return (hour, minute) as integers
# returns a tuple of (hour: int, minute: int)
def parse_time(time_str):
    parts = time_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid time format: {time_str}")
    
    hour = int(parts[0])
    minute = int(parts[1])
    
    return hour, minute

# function to check if a time string represents an evening slot (18:00 or later)
# returns True if evening slot, False otherwise
def is_evening_time(time_str):
    from .constants import EVENING_HOUR_THRESHOLD
    
    hour, _ = parse_time(time_str)
    return hour >= EVENING_HOUR_THRESHOLD

# function to parse a boolean string (true/false)
# returns True or False
def parse_boolean(value_str):
    value_str = value_str.strip().lower()
    if value_str == "true":
        return True
    elif value_str == "false":
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value_str}")

# function to check if a line is empty or contains only whitespace
# returns True if empty, False otherwise
def is_empty_line(line):
    return not line or line.strip() == ""

# function to normalize an event ID by stripping extra whitespace
# returns normalized event identifier
def normalize_event_id(event_id):
    # split by spaces and rejoin to normalize multiple spaces
    parts = event_id.split()
    return ' '.join(parts)