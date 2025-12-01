from collections import defaultdict
from model.schedule import Schedule
from parser.problem_instance import ProblemInstance
from parser.slot import LectureSlot, TutorialSlot
from eval.eval import eval, eval_pref, eval_pair, eval_minfilled, eval_secdiff
from eval.hard_constraints import Valid

"""
    Contains the functions that will select a parent via roulette wheel selection
"""

def fitness(schedule, problem, w_hard, w_soft):
    """
    Assigns a fitness score to an individual schedule
        - need weights: w_hard for valid/hard constraints, w_soft for eval/soft constraints
    To be used to select parent(s)
    """
    valid_value = Valid(schedule, problem)
    eval_value = eval(schedule, problem)

    # closer to 1 is more fit
    # fit = 1 an optimal solution => can return
    fitness_value = 1 / (1 + (w_hard * valid_value) + (w_soft * eval_value))

    return fitness_value


def probability(f, problem):
    """
    Input: the entire set of facts
    Outputs: a probability value (chance to be selected as parent) assigned to individual schedule
    """
    new_f = defaultdict(list)
    # 1. find the fitness value for each schedule
    for schedule in f:
        fit_value = fitness(schedule, problem, 100, 1)
        new_f[schedule] = fit_value

    # 2. sum of all fitness scores from all schedules in our set of facts
    total_prob = sum(new_f.values())

    # 3. the probability of schedule being chosen is its fitness value / sum of all fitness values
    for schedule in new_f:
        prob_value = new_f[schedule] / total_prob
        new_f[schedule] = prob_value

    return new_f


def running_sum(f, problem):
    return None