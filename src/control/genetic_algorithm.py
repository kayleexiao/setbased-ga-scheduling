import math
import random
from eval.eval import eval as soft_eval
from eval.hard_constraints import (
    Valid, PassEvening, PassAL, PassLectures, PassTutorials, _check_5xx_lectures, _check_not_compatible
)
from eval.selection import fitness, probability, running_sum
from model.initial_state import generate_initial_state
from model.extension_rules import (
    mutate_evening, mutate_AL, mutate_lecture, mutate_tutorial, mutate_500_conflict, mutate_notcompatible,
    crossover, purge
)
from control.repair import repair_schedule


class GeneticAlgorithm:

    def __init__(
        self,
        problem_instance,
        max_valid_solutions=1,
        p_mutation=0.5,
        w_hard=3000,
        w_soft=1
    ):  
        self.problem = problem_instance
        self.max_valid_solutions = max_valid_solutions
        self.p_mutation = p_mutation
        self.w_hard = w_hard
        self.w_soft = w_soft
        
        # scale bounding parameters based on problem size
        scaled_max_gen, scaled_plateau, scaled_population_size = self.scale_bounding_parameters()
        self.population_size = scaled_population_size
        self.max_generations = scaled_max_gen
        self.plateau_limit = scaled_plateau

        # mutation mapping for fallback
        self.all_mutations = {
            "evening": mutate_evening,
            "al": mutate_AL,
            "lecture": mutate_lecture,
            "tutorial": mutate_tutorial,

            "500fix": lambda s, sl: mutate_500_conflict(s, sl, self.problem),
            "notcompat": lambda s, sl: mutate_notcompatible(s, sl, self.problem),
        }

        # counters
        self.generation = 0
        self.plateau_counter = 0
        self.valid_found = 0

    # Tournament selection
    def tournament(self, population, k=25):

        # randomly pick k candidates from population
        competitors = random.sample(population, k)

        # sort them by fitness (3rd item in tuple)
        competitors.sort(key=lambda x: x[2], reverse=True)

        # return only the schedule object of the winner
        return competitors[0][0] 

    # =====================================================================
    # Main GA
    # =====================================================================
    def run(self, print_interval=50):
        print("\n=== GENERATING INITIAL POPULATION ===")

        # build initial population with weighted hard/soft evaluation
        population = generate_initial_state(
            self.problem,
            self.population_size,
            w_hard=self.w_hard,
            w_soft=self.w_soft
        )

        # Convert evals to probs
        population = probability(running_sum(population))
        best_fitness_before = None

        print("\n=== BEGIN GA EVOLUTION ===")

        # ==========================================================
        # Main loop
        # ==========================================================
        for self.generation in range(self.max_generations):

            # sort individuals by fitness
            population.sort(key=lambda x: x[2], reverse=True)

            # current best individual
            elite = population[0]

            # unpack fields
            best_schedule, best_eval, best_fitness, _ = elite

            # hard penalty count
            best_valid = Valid(best_schedule, self.problem)

            # Periodically print progress
            if self.generation % print_interval == 0:
                print(
                    f"[gen {self.generation:4d}] "
                    f"fitness={best_fitness:.4f}  "
                    f"hard={best_valid}  "
                    f"soft={best_eval}"
                )

            # plateau logic
            if best_fitness_before is not None:
                if best_fitness <= best_fitness_before:

                    # stagnation detected
                    self.plateau_counter += 1

                else:

                    # improvement resets counter
                    self.plateau_counter = 0

            best_fitness_before = best_fitness

            # terminate if no improvement for plateau_limit generations
            if self.plateau_counter >= self.plateau_limit:
                print("\n[GA] Plateau reached — terminating.")
                break

            # terminate early if optimal is schedule found
            if best_fitness == 1.0:
                print(f"\n[GA] Optimal schedule found at generation {self.generation}")
                break

            # maintain population size
            if len(population) > self.population_size:
                population = purge(population, len(population) - self.population_size)

            # recompute probs
            population = probability(running_sum(population))

            # Extensions
            if random.random() < self.p_mutation:

                # select parent
                parent = self.tournament(population)

                # Decide which mutation to use
                mut_type = self.choose_mutation_type(parent)

                # Debug
                if self.generation % 500 == 0:
                    print(f"[DEBUG] gen {self.generation}: mutating '{mut_type}' "
                        f"(Evening={PassEvening(parent, self.problem)}, "
                        f"AL={PassAL(parent, self.problem)}, "
                        f"Lect={PassLectures(parent, self.problem)}, "
                        f"Tut={PassTutorials(parent, self.problem)})")
                    
                # mutation function
                mut_fn = self.all_mutations[mut_type]

                # all possible slot options
                all_slots = (
                    list(self.problem.lec_slots_by_key.values()) +
                    list(self.problem.tut_slots_by_key.values())
                )

                child = None
                attempts = 0

                # attempt mutation up to 5 times
                while child is None and attempts < 5:
                    candidate = mut_fn(parent, all_slots)
                    if candidate is not None:
                        # Run repair immediately on mutated schedule
                        child = repair_schedule(candidate, self.problem)
                    attempts += 1

                if child is None:
                    # fallback if requested mutation fails
                    alt_types = ["lecture", "tutorial"]
                    random.shuffle(alt_types)

                    for alt in alt_types:
                        if alt not in self.all_mutations:
                            continue
                        alt_fn = self.all_mutations[alt]
                        candidate = alt_fn(parent, all_slots)
                        if candidate is not None:
                            child = repair_schedule(candidate, self.problem)
                            break

            else:
                # crossover
                p1 = self.tournament(population)
                p2 = self.tournament(population)
                while p2 == p1: # ensuring two unique parents are selected
                    p2 = self.tournament(population)


                # build new schedule by combining parents
                child = crossover(p1, p2)

                # repair any structural issues
                child = repair_schedule(child, self.problem)

            # evaluate child
            child_eval = soft_eval(child, self.problem)
            schedule, eval_v, fit_v, _ = fitness(
                (child, child_eval, 0, 0),
                self.problem,
                self.w_hard,
                self.w_soft
            )

            population.append((schedule, eval_v, fit_v, 0))

            # ensure best survives
            population.sort(key=lambda x: x[2], reverse=True)
            if population[0] != elite:
                population[-1] = elite

        # debug print, if max generation limit was reached
        else:
            print("\n[GA] Maximum generations reached — terminating.")

        # ==========================================================
        # Best valid schedule
        # ==========================================================
        population.sort(key=lambda x: x[2], reverse=True)
        best_schedule, best_eval, best_fitness, _ = population[0]
        best_valid = Valid(best_schedule, self.problem)

        print("\n=== GA FINISHED ===")
        print(f"Generations: {self.generation}")
        print(f"Best fitness : {best_fitness:.4f}")
        print(f"Hard penalty : {best_valid}")
        print(f"Soft penalty : {best_eval}")

        return best_schedule, best_eval, best_valid, best_fitness
    
    # Robust mutation selection 
    def choose_mutation_type(self, schedule):
        failing = []

        if _check_5xx_lectures(schedule, self.problem) > 0:
            failing.append("500fix")

        if _check_not_compatible(schedule, self.problem) > 0:
            failing.append("notcompat")

        if not PassEvening(schedule, self.problem):
            failing.append("evening")

        if not PassAL(schedule, self.problem):
            failing.append("al")

        if not PassLectures(schedule, self.problem):
            failing.append("lecture")

        if not PassTutorials(schedule, self.problem):
            failing.append("tutorial")

        if failing:
            return random.choice(failing)

        return random.choice(list(self.all_mutations.keys()))
    

    def scale_bounding_parameters(self):

        # getting problem size
        events_count = len(self.problem.get_all_event_ids())
        slots_count = (len(self.problem.get_all_lecture_slot_keys()) + len(self.problem.get_all_tutorial_slot_keys()))

        # scaling the bounding parameters based on the problem size
        max_generations = max(50000, int(300 * events_count * math.log(slots_count + 1))) # minimum bound of 50k max generations, log is used to avoid extreme growth
        plateau_limit = max(50000, int(20 * events_count)) # minimum plateau limit of 50k, problem size increases the limit linearly
        population_size = population_size = max(250, min(500, int(events_count * 5))) # population size between 250 and 500, scales linearly with problem size

        print(f"\n[GA] Search Bounds | max_generations={max_generations}, plateau_limit={plateau_limit}, population_size={population_size}")

        return max_generations, plateau_limit, population_size


