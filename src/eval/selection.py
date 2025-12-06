from eval.hard_constraints import Valid

"""
    Contains the functions that will select a parent via roulette wheel selection
    fitness and eval used upon schedule creation
"""

def fitness(f, problem, w_hard, w_soft):
    """
    Assigns a fitness score to an individual schedule
        - need weights: w_hard for valid/hard constraints, w_soft for eval/soft constraints
        - f = (Schdule, eval_value, fit_value, probability)
        - assuming eval value has already been calculated
    To be used to select parent(s)
    """
    schedule, eval_value, fit_value, probability = f

    valid_value = Valid(schedule, problem)

    # closer to 1 is more fit
    # fit = 1 an optimal solution => can return
    new_fit_value = 1 / (1 + (w_hard * valid_value) + (w_soft * eval_value))

    return (schedule, eval_value, new_fit_value, probability)


def probability(f):
    """
    Input: the entire set of facts
        - each tuple = (Schedule, eval_value, fit_value, probability=0)
    Outputs: a probability value (chance to be selected as parent) assigned to individual schedule
    """
    # 1. sum of all fitness scores from all schedules in our set of facts
    # indivdiual fit already computed at this point
    total_fit = sum(individual[2] for individual in f)

    # returning new F with updated probability for each schedule
    new_f = []

    # 2. the probability of schedule being chosen is its fitness value / sum of all fitness values
    for schedule, eval_value, fit_value, probability in f:
        new_prob = fit_value / total_fit
        new_f.append((schedule, eval_value, fit_value, new_prob))
        
    return new_f


def running_sum(f):
    """
    builds the cumulative (running) sum over the probabilities!
    input: f: [(schedule, eval_value, fit_value, probability), ...]
    output: new_f: [(schedule, eval_value, fit_value, cumulative_probability), ...]
    """
    new_f = []
    running_total = 0.0

    for schedule, eval_value, fit_value, prob in f:
        running_total += prob
        new_f.append((schedule, eval_value, fit_value, running_total))

    # force the last cumulative probability to be exactly 1.0 (just to avoid float issues lol)
    if new_f:
        schedule, eval_value, fit_value, _ = new_f[-1]
        new_f[-1] = (schedule, eval_value, fit_value, 1.0)

    return new_f