import os
import sys

TESTFILE = "deptinst1.txt"

def find_project_root(start_dir):
    cur = os.path.abspath(start_dir)
    while True:
        if os.path.isdir(os.path.join(cur, "src")) and os.path.isdir(os.path.join(cur, "input")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            raise RuntimeError("Project root not found (no src/ or input/ folders detected).")
        cur = parent

ROOT = find_project_root(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(ROOT, "src"))

from parser.parser import parse_from_command_line
from control.genetic_algorithm import GeneticAlgorithm
from eval.hard_constraints import Valid
from eval.eval import eval as soft_eval


def test_ga():
    input_path = os.path.join(ROOT, "input", TESTFILE)

    print("=== PARSING INPUT FILE ===")
    print(f"Using test input: {input_path}\n")

    args = [
        input_path,
        "1", "0", "1", "0",
        "10", "10", "10", "10"
    ]

    problem = parse_from_command_line(args)
    print(f"Loaded Problem: {problem.name}\n")

    ga = GeneticAlgorithm(problem)
    best_schedule, best_soft, best_hard = ga.run(print_interval=200)
    ga.debug_hard_constraints(best_schedule)

    print("\n=== BEST SCHEDULE RESULTS ===")
    print(f"Hard violations   : {best_hard}")
    print(f"Soft penalty      : {best_soft}")

    print(">> VALID schedule found!" if best_hard == 0 else ">> No valid schedule (best attempt shown).")


if __name__ == "__main__":
    test_ga()
