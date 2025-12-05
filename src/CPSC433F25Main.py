import os
import sys

# Require a filename as a command-line argument
if len(sys.argv) < 2:
    print("Error: Please provide an input file.\n")
    print("Usage: python src/ga_driver.py <input_file>")
    sys.exit(1)

TESTFILE = sys.argv[1]

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
from eval.hard_constraints import Valid, _check_5xx_lectures, _check_5xx_time_overlap, _check_active_learning_requirements, _check_capacity, _check_department_blackout, _check_evening_rules, _check_not_compatible, _check_partial_assignments, _check_tutorials_section_diff_from_lecture, _check_unwanted
from eval.eval import eval as soft_eval


def start_search():
    input_path = os.path.join(ROOT, "input", TESTFILE)

    args = [
        input_path,
        sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
        sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9]
    ]

    problem = parse_from_command_line(args)

    ga = GeneticAlgorithm(problem)
    best_schedule, best_soft, best_hard = ga.run(print_interval=200)

    from eval.hard_constraints import debug_all_hard_constraints
    debug_all_hard_constraints(best_schedule, problem)

    print("=== BEST SCHEDULE RESULTS ===")
    print(f"Hard violations   : {best_hard}")
    print(f"Soft penalty      : {best_soft}")

    print(">> VALID schedule found!" if best_hard == 0 else ">> No valid schedule (best attempt shown).")

    print_schedule_formatted(best_schedule, problem, best_soft)

# Print the schedule grouped by lecture and its tutorials
# Should be able to reuse this for final version
def print_schedule_formatted(schedule, problem, eval_value):

    print("\n================ FORMATTED SCHEDULE ASSIGNMENT ================\n")
    
    print(f"Eval-value: {eval_value}")

    all_keys = set(problem.course_list.keys()) | set(problem.tut_list.keys())
    course_keys = sorted(all_keys, key=lambda k: (k[0], int(k[1])))
    #course_keys = sorted(problem.course_list.keys(), key=lambda k: (k[0], int(k[1])))

    rows = []
                

    for (dept, num) in course_keys:

        # Skip if this course has no lectures
            if (dept, num) not in problem.course_list:
                continue

            lec_ids = sorted(problem.course_list[(dept, num)])
            for lec_id in lec_ids:
                lec_ev = problem.get_event(lec_id)
                slot = schedule.get_assignment(lec_ev)
                right = f"{slot.day}, {slot.start_time}"

                left = f"{dept} {num} {lec_ev.section_label}"
                rows.append((left, right, (dept, num)))

                # tutorials for this lecture
                tut_ids = sorted(problem.tut_list.get((dept, num), []))
                for tut_id in tut_ids:
                    tut_ev = problem.get_event(tut_id)

                    if tut_ev.section_label != lec_ev.section_label:
                        continue

                    tut_slot = schedule.get_assignment(tut_ev)
                    left2 = f"{dept} {num} {lec_ev.section_label} {tut_ev.tutorial_label}"
                    right2 = f"{tut_slot.day}, {tut_slot.start_time}"
                    rows.append((left2, right2, (dept, num)))

    # Also include special courses (CPSC 851, CPSC 913)
    for (dept, num) in course_keys:
        if (dept, num) not in problem.course_list and (dept, num) in problem.tut_list:
            for tut_id in sorted(problem.tut_list[(dept, num)]):
                tut_ev = problem.get_event(tut_id)
                slot = schedule.get_assignment(tut_ev)

                left = f"{dept} {num} {tut_ev.tutorial_label}"
                right = f"{slot.day}, {slot.start_time}"
                rows.append((left, right, (dept, num)))

    # compute alignment width
    max_left = max(len(left) for left, _, _ in rows)

    # print that jawn
    last_course = None

    for left, right, ck in rows:
        if last_course and ck != last_course:
            print()
        print(f"{left.ljust(max_left)} : {right}")
        last_course = ck

    print("\n=======================================================\n")



if __name__ == "__main__":
    start_search()
