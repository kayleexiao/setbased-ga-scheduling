# Section headers from input file
SECTION_HEADERS = [
    "Name:",
    "Lecture slots:",
    "Tutorial slots:",
    "Lectures:",
    "Tutorials:",
    "Not compatible:",
    "Unwanted:",
    "Preferences:",
    "Pair:",
    "Partial assignments:",
]

# Reads raw input and returns a list of strings
# Each string is one line from the file
def read_all_lines(path: str) -> list[str]:
    with open(path, "r") as f:
        # Strip whitespace and newline characters from each line
        return [line.strip() for line in f.readlines()]


# Takes list produced by read_all_lines() and divides it into a
# dictionary of sections.
def split_into_sections(lines: list[str]) -> dict[str, list[str]]:
    # Final output dictionary
    sections = {} 
    # Keeps track of what section we are in
    current_header = None
    # Collects lines in current section
    buffer = []

    # Main loop
    for line in lines:

        if line in SECTION_HEADERS:

            if current_header is not None:
                sections[current_header] = buffer

            # Init new section
            current_header = line
            # Prepare buffer
            buffer = []

        else:
            # Collect all lines in current section
            if current_header is not None and line != "":
                buffer.append(line)
    
    # Save last buffered section
    if current_header is not None:
        sections[current_header] = buffer
    
    return sections