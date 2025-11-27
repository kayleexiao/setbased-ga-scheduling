import sys
import os
import traceback

# add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from parser.parser import parse_input_file
from model.schedule import Schedule
from parser.event import Event
from eval.eval import eval, eval_pref, eval_pair, eval_minfilled, eval_secdiff

# test on input1.txt
def test_eval(input_file="input/input1.txt"):

    try:
        # parse the input1.txt file -> create problem instance
        problem = parse_input_file(
            input_file,
            pen_lecturemin=10,
            pen_tutorialmin=10,
            pen_notpaired=10,
            pen_section=10,
            w_minfilled=1,
            w_pref=1,
            w_pair=1,
            w_secdiff=1
        )
        print("File parsed, problem instance created")

        # create mock schedule from problem
        schedule = create_schedule(problem)
        print(schedule)
        # for this schedule
        # minfilled = 20
        # section = 10
        # pref = 3

        eval_value = eval(schedule, problem)
        print(eval_value)

    except Exception: 
        print("Error")
        traceback.print_exc()
        return None
    

def create_schedule(problem):
    schedule = Schedule()

    # assigning lectures -> 2 * penalty_minfilled as MO 9:00 is unfilled
    schedule.assign(problem.lec_by_id["CPSC 231 LEC 01"], problem.lec_slots_by_key[("LEC", "TU", "9:30")])
    schedule.assign(problem.lec_by_id["CPSC 231 LEC 02"], problem.lec_slots_by_key[("LEC", "TU", "9:30")])
    schedule.assign(problem.lec_by_id["DATA 201 LEC 01"], problem.lec_slots_by_key[("LEC", "MO", "8:00")])
    schedule.assign(problem.lec_by_id["SENG 300 LEC 01"], problem.lec_slots_by_key[("LEC", "MO", "8:00")])

    # assigning tutorials - no minfilled penalty
    schedule.assign(problem.tut_by_id["CPSC 231 LEC 01 TUT 01"], problem.tut_slots_by_key[("TUT", "FR", "10:00")])
    schedule.assign(problem.tut_by_id["CPSC 231 LEC 02 TUT 02"], problem.tut_slots_by_key[("TUT", "TU", "10:00")])
    schedule.assign(problem.tut_by_id["DATA 201 LEC 01 LAB 01"], problem.tut_slots_by_key[("TUT", "MO", "8:00")])
    schedule.assign(problem.tut_by_id["SENG 300 TUT 01"], problem.tut_slots_by_key[("TUT", "MO", "8:00")])

    # only penalties should be penalty_secdiff for CPSC 231 LEC 01/02 being in same slot and penalty_minfilled for MO 9:00
    # penalty = 30
    return schedule

if __name__ == "__main__":
    test_eval()

