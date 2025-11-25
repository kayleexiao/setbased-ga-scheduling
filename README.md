# CPSC 433 – Set-Based Genetic Algorithm Search Scheduling

This repository contains our implementation of the set-based search model for the CPSC 433 course scheduling project.

## Group Members: Team Turtwig

- John Cummings 30219471
- Victor Nguyen 30171290
- Stephanie Sevilla 30176781
- Jacob Situ 30144935
- Kaylee Xiao 30173778
- Raza Zaidi 30075408

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

When working under these branches, create sub-branches, e.g., `feature/parser/xxx-xxx`.
