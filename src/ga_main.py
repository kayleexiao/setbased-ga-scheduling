import os
import sys

from parser.parser import parse_from_command_line
from control.genetic_algorithm import GeneticAlgorithm


# Require a filename as a command-line argument
if len(sys.argv) < 2:
    print("Error: Please provide an input file with weights and penalties.\n")
    print("Usage: python src/ga_main.py <input_file> <w_minfilled> <w_pref> <w_pair> <w_secdiff> <pen_lecturemin> <pen_tutorialmin> <pen_notpaired> <pen_section>")
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

def start_search():
    input_path = os.path.join(ROOT, "input", TESTFILE)

    args = [
        input_path,
        sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
        sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9]
    ]

    problem = parse_from_command_line(args)

    ga = GeneticAlgorithm(problem)
    best_schedule, best_soft, best_hard, best_fitness = ga.run(print_interval=200)

    from eval.hard_constraints import debug_all_hard_constraints
    debug_all_hard_constraints(best_schedule, problem)

    print("=== BEST SCHEDULE RESULTS ===")
    print(f"Hard violations   : {best_hard}")
    print(f"Soft penalty      : {best_soft}")

    print(">> VALID schedule found!" if best_hard == 0 else ">> No valid schedule (best attempt shown).")

    print_schedule_formatted(best_schedule, problem, best_soft)
    
    write_output_to_file(
        input_filename=TESTFILE,
        best_schedule=best_schedule,
        best_soft=best_soft,
        best_hard=best_hard,
        generation=ga.generation,
        best_fitness=best_fitness,
        problem=problem,
        root_dir=ROOT
    )

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

def write_output_to_file(input_filename, best_schedule, best_soft, best_hard, generation, best_fitness, problem, root_dir, output_dir="output"):
    """
    Write the final GA results and formatted schedule to a text file.
    
    Args:
        input_filename: Name of the input file (e.g., 'test1.txt')
        best_schedule: The best schedule found
        best_soft: Soft constraint penalty value
        best_hard: Hard constraint violation count
        generation: Final generation number
        best_fitness: Best fitness value achieved
        problem: Problem instance
        root_dir: Project root directory
        output_dir: Directory to write output file (default: 'output')
    """
    import os
    
    # create output directory if it doesn't exist
    output_path_dir = os.path.join(root_dir, output_dir)
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
    
    # generate output filename from input filename
    base_name = os.path.splitext(input_filename)[0]
    output_filename = f"{base_name}_output.txt"
    output_path = os.path.join(output_path_dir, output_filename)
    
    with open(output_path, 'w') as f:
        # write GA summary
        f.write("=== GA RESULTS ===\n")
        f.write(f"Generations: {generation}\n")
        f.write(f"Best fitness : {best_fitness:.4f}\n")
        f.write(f"Hard penalty : {best_hard}\n")
        f.write(f"Soft penalty : {best_soft}\n")
        f.write("\n")
        
        # write schedule validity
        if best_hard == 0:
            f.write(">> VALID schedule found!\n")
        else:
            f.write(">> No valid schedule (best attempt shown).\n")
        f.write("\n")
        
        # write formatted schedule
        f.write("================ FORMATTED SCHEDULE ASSIGNMENT ================\n\n")
        f.write(f"Eval-value: {best_soft}\n")
        
        # get all course keys
        all_keys = set(problem.course_list.keys()) | set(problem.tut_list.keys())
        course_keys = sorted(all_keys, key=lambda k: (k[0], int(k[1])))
        
        rows = []
        
        # build rows for courses with lectures
        for (dept, num) in course_keys:
            if (dept, num) not in problem.course_list:
                continue
            
            lec_ids = sorted(problem.course_list[(dept, num)])
            for lec_id in lec_ids:
                lec_ev = problem.get_event(lec_id)
                slot = best_schedule.get_assignment(lec_ev)
                right = f"{slot.day}, {slot.start_time}"
                left = f"{dept} {num} {lec_ev.section_label}"
                rows.append((left, right, (dept, num)))
                
                # add tutorials for this lecture
                tut_ids = sorted(problem.tut_list.get((dept, num), []))
                for tut_id in tut_ids:
                    tut_ev = problem.get_event(tut_id)
                    
                    if tut_ev.section_label != lec_ev.section_label:
                        continue
                    
                    tut_slot = best_schedule.get_assignment(tut_ev)
                    left2 = f"{dept} {num} {lec_ev.section_label} {tut_ev.tutorial_label}"
                    right2 = f"{tut_slot.day}, {tut_slot.start_time}"
                    rows.append((left2, right2, (dept, num)))
        
        # add special courses (tutorials without lectures, e.g., CPSC 851, CPSC 913)
        for (dept, num) in course_keys:
            if (dept, num) not in problem.course_list and (dept, num) in problem.tut_list:
                for tut_id in sorted(problem.tut_list[(dept, num)]):
                    tut_ev = problem.get_event(tut_id)
                    slot = best_schedule.get_assignment(tut_ev)
                    left = f"{dept} {num} {tut_ev.tutorial_label}"
                    right = f"{slot.day}, {slot.start_time}"
                    rows.append((left, right, (dept, num)))
        
        # calculate alignment width
        max_left = max(len(left) for left, _, _ in rows)
        
        # write formatted rows
        last_course = None
        for left, right, ck in rows:
            if last_course and ck != last_course:
                f.write("\n")
            f.write(f"{left.ljust(max_left)} : {right}\n")
            last_course = ck
        
        f.write("\n=======================================================\n")
    
    print(f"\n[OUTPUT] Results written to: {output_path}")
    return output_path

if __name__ == "__main__":
    start_search()
