import sys
import os

# add src directory to Python path (same pattern as test_eval.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from parser.parser import parse_input_file
from eval.selection import probability, running_sum
from model.initial_state import generate_initial_state


def check(cond, msg):
    if cond:
        print(f"PASS: {msg}")
    else:
        print(f"FAIL: {msg}")
        raise AssertionError(msg)


def test_selection():
    # parse the same input file used in test_eval
    input_path = os.path.join(project_root, "input", "input3.txt")

    problem = parse_input_file(
        input_path,
        pen_lecturemin=10,
        pen_tutorialmin=10,
        pen_notpaired=10,
        pen_section=10,
        w_minfilled=1,
        w_pref=1,
        w_pair=1,
        w_secdiff=1,
    )
    print("Problem parsed for selection test")

    #  generate a small initial population of facts
    # each fact = (schedule, eval_value, fitness_value, probability)
    population = generate_initial_state(
        problem_instance=problem,
        k=5,
        w_hard=10,
        w_soft=1,
        seed=42,   # make it reproducible
    )
    print(f"Generated {len(population)} schedules")

    # compute probabilities from fitness
    pop_with_probs = probability(population)

    probs = [p for (_, _, _, p) in pop_with_probs]
    print("Individual probabilities:", probs)

    # they should sum to ~1
    check(abs(sum(probs) - 1.0) < 1e-6, "probabilities sum to 1.0")

    # 4. compute running sum (cumulative probabilities)
    cumulative = running_sum(pop_with_probs)
    cum_probs = [p for (_, _, _, p) in cumulative]

    print("Cumulative probs:", cum_probs)

    # cumulative probs must be non-decreasing
    for i in range(1, len(cum_probs)):
        check(cum_probs[i] >= cum_probs[i - 1], f"cum_probs[{i}] >= cum_probs[{i-1}]")

    # last cumulative prob should be exactly 1.0 (your code forces this)
    check(abs(cum_probs[-1] - 1.0) < 1e-6, "last cumulative prob is 1.0")

    print("\nSelection tests completed successfully.\n")


if __name__ == "__main__":
    test_selection()
