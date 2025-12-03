import random
from eval.eval import eval as soft_eval
from eval.hard_constraints import (
    Valid, PassEvening, PassAL, PassLectures, PassTutorials
)
from eval.selection import fitness, probability, running_sum
from model.initial_state import generate_initial_state
from model.extension_rules import (
    mutate_evening, mutate_AL, mutate_lecture, mutate_tutorial,
    crossover, purge
)


class GeneticAlgorithm:

    def __init__(
        self,
        problem_instance,
        population_size=150,
        max_generations=20000,
        max_valid_solutions=1,
        plateau_limit=20000,
        p_mutation=0.5,
        w_hard=3000,
        w_soft=1
    ):
        self.problem = problem_instance
        self.population_size = population_size
        self.max_generations = max_generations
        self.max_valid_solutions = max_valid_solutions
        self.plateau_limit = plateau_limit
        self.p_mutation = p_mutation
        self.w_hard = w_hard
        self.w_soft = w_soft

        # mutation mapping for fallback
        self.all_mutations = {
            "evening": mutate_evening,
            "al": mutate_AL,
            "lecture": mutate_lecture,
            "tutorial": mutate_tutorial,
        }

        # counters
        self.generation = 0
        self.plateau_counter = 0
        self.valid_found = 0

    # Tournament selection
    def tournament(self, population, k=4):
        competitors = random.sample(population, k)
        competitors.sort(key=lambda x: x[2], reverse=True)
        return competitors[0][0]  # return schedule only


    # =====================================================================
    # Main GA
    # =====================================================================
    def run(self, print_interval=50):
        print("\n=== GENERATING INITIAL POPULATION ===")
        population = generate_initial_state(
            self.problem,
            self.population_size,
            w_hard=self.w_hard,
            w_soft=self.w_soft
        )

        population = probability(running_sum(population))
        best_fitness_before = None

        print("\n=== BEGIN GA EVOLUTION ===")

        # ==========================================================
        # Main loop
        # ==========================================================
        for self.generation in range(self.max_generations):

            # sort population
            population.sort(key=lambda x: x[2], reverse=True)
            elite = population[0]
            best_schedule, best_eval, best_fitness, _ = elite
            best_valid = Valid(best_schedule, self.problem)

            # progress print
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
                    self.plateau_counter += 1
                else:
                    self.plateau_counter = 0
            best_fitness_before = best_fitness

            if self.plateau_counter >= self.plateau_limit:
                print("\n[GA] Plateau reached — terminating.")
                break

            # found valid schedule
            if best_valid == 0:
                print(f"[GA] VALID schedule found at generation {self.generation}")
                break

            # maintain population size
            if len(population) > self.population_size:
                population = purge(population, len(population) - self.population_size)

            # recompute probs
            population = probability(running_sum(population))

            # Extensions
            if random.random() < self.p_mutation:
                # mutation
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

                mut_fn = self.all_mutations[mut_type]

                all_slots = (
                    list(self.problem.lec_slots_by_key.values()) +
                    list(self.problem.tut_slots_by_key.values())
                )

                child = None
                attempts = 0

                # Try a few times with the chosen type
                # if we get None, fall back to more generic mutation or crossover
                while child is None and attempts < 5:
                    child = mut_fn(parent, all_slots)
                    attempts += 1

                if child is None:
                    # Fallback 
                    # either try a generic lecture/tutorial mutation, or just do crossover as a last resort to keep search moving
                    alt_types = ["lecture", "tutorial"]
                    random.shuffle(alt_types)

                    for alt in alt_types:
                        alt_fn = self.all_mutations[alt]
                        child = alt_fn(parent, all_slots)
                        if child is not None:
                            break

            else:
                # crossover
                p1 = self.tournament(population)
                p2 = self.tournament(population)
                child = crossover(p1, p2)

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

        return best_schedule, best_eval, best_valid
    
    # Choose which mutation sub-extension to apply
    def choose_mutation_type(self, schedule):
        """
        Decide which mutation sub-extension to use based on which
        hard-constraint categories are currently failing.
            - Cevening   -> mutate_evening
            - CAL        -> mutate_AL
            - Clectures  -> mutate_lecture
            - Ctutorials -> mutate_tutorial
        """
        needed = []

        if not PassEvening(schedule, self.problem):
            needed.append("evening")

        if not PassAL(schedule, self.problem):
            needed.append("al")

        if not PassLectures(schedule, self.problem):
            needed.append("lecture")

        if not PassTutorials(schedule, self.problem):
            needed.append("tutorial")

        # If all hard constraint categories pass (i wish) pick random
        if not needed:
            needed = ["lecture", "tutorial", "evening", "al"]

        return random.choice(needed)

    # Hard constrain debug
    def debug_hard_constraints(self, schedule):

        from eval.hard_constraints import (
            _check_capacity,
            _check_not_compatible,
            _check_unwanted,
            _check_partial_assignments,
            _check_active_learning_requirements,
            _check_evening_rules,
            _check_department_blackout,
            _check_5xx_lecures,
            _check_tutorials_section_diff_from_lecture,
        )

        problem = self.problem

        c_capacity      = _check_capacity(schedule, problem)
        c_notcomp       = _check_not_compatible(schedule, problem)
        c_unwanted      = _check_unwanted(schedule, problem)
        c_partial       = _check_partial_assignments(schedule, problem)
        c_al_req        = _check_active_learning_requirements(schedule, problem)
        c_evening       = _check_evening_rules(schedule, problem)
        c_blackout      = _check_department_blackout(schedule, problem)
        c_5xx           = _check_5xx_lecures(schedule, problem)
        c_tut_sec_diff  = _check_tutorials_section_diff_from_lecture(schedule, problem)

        total = (
            c_capacity + c_notcomp + c_unwanted + c_partial +
            c_al_req + c_evening + c_blackout + c_5xx + c_tut_sec_diff
        )

        print("\n================ HARD CONSTRAINT DEBUG ================")
        print(f"Total Hard Penalty = {total}\n")

        print("---- C1/C8/C14/C15: Capacity ------------------------")
        print(f"Capacity violations            : {c_capacity}")

        print("\n---- C2: Not Compatible -----------------------------")
        print(f"NotCompatible violations       : {c_notcomp}")

        print("\n---- C3: Partial Assignments ------------------------")
        print(f"Partial assignment violations  : {c_partial}")

        print("\n---- C4: Unwanted -----------------------------------")
        print(f"Unwanted violations            : {c_unwanted}")

        print("\n---- C5: 500-Level Lecture Conflicts ----------------")
        print(f"5xx lecture conflicts          : {c_5xx}")

        print("\n---- C9: Tutorial Same Slot as Lecture --------------")
        print(f"TUT same-slot-as-LEC           : {c_tut_sec_diff}")

        print("\n---- C16: Active Learning ----------------------------")
        print(f"AL requirement violations      : {c_al_req}")

        print("\n---- C11–C13: Evening Rules --------------------------")
        print(f"Evening rule violations        : {c_evening}")

        print("\n---- C6: Department Blackout -------------------------")
        print(f"Dept blackout violations       : {c_blackout}")

        print("\n================ END HARD CONSTRAINT DEBUG ================\n")
