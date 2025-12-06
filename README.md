# CPSC 433 – Set-Based Genetic Algorithm Search Scheduling

This repository contains our implementation of the genetic algorithms set-based search model for the CPSC 433 course scheduling project.

## Group Members: Team Turtwig

- John Cummings 30219471
- Victor Nguyen 30171290
- Stephanie Sevilla 30176781
- Jacob Situ 30144935
- Kaylee Xiao 30173778
- Raza Zaidi 30075408

## Set Up
Place all input files in the `input/` directory.

To run the program from the project root:
```
python src/ga_main.py <input_file> <w_minfilled> <w_pref> <w_pair> <w_secdiff> <pen_lecturemin> <pen_tutorialmin> <pen_notpaired> <pen_section>
```

Example: ```python src/CPSC433F25Main.py input.txt 1 1 1 1 1 1 1 1```

## Repository Structure
```
input/      # .txt instance files
output/     # program output (final schedules, eval values)
src/        # main project source code (parser, problem instance, eval, search, etc.)
tests/      # small local tests for parser, eval, search components, etc.
```

## Branch Setup
**LET'S NOT BREAK MAIN!!** Here is the branch flow we'll use:
- `main` : stable branch, only merge here when a component is complete and reviewed
- `feature/parser-main`: all input parsing code and ProblemInstance construction
- `feature/model-main`: event objects, slot objects, state representation, assignment facts
- `feature/eval-main`: eval function and all soft-constraint subfunctions
- `feature/control-main`: search rules, schedule generation, and set-based search control logic
- `feature/output-main`: printing final schedules in required format

