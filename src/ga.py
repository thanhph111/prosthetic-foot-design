"""Main script to run optimization program by using genetic algorithm.
"""

# Standard modules
import os
import sys
import random
import copy
import subprocess
import ast
import json
import glob
import time
import concurrent.futures

# User modules
import sub.plot as plot
from sub.inputprocess import DOMAINS
from sub.inputprocess import CONSTRAINTS
from sub.inputprocess import CONSTANTS as CONS


CHROMOSOME_SIZE = len(DOMAINS)
CONSTANTS = [
    DOMAINS,
    CONSTRAINTS,
    CHROMOSOME_SIZE,
    CONS["GENERATION_SIZE"],
    CONS["POPULATION_SIZE"],
    CONS["SELECTION_RATE"],
    CONS["CALCULATE_MODE"],
    CONS["MUTATION_MODE"],
    CONS["MAJOR_MUTATION_RATE"],
    CONS["MINOR_MUTATION_RATE"],
    CONS["AMP_FACT"],
]


COLORS = {
    "HEADER": "\033[95m",
    "OKBLUE": "\033[94m",
    "OKGREEN": "\033[92m",
    "WARNING": "\033[93m",
    "FAIL": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}


class Chromosome:
    def __init__(self):
        self.genes = self.domains_to_genes()
        self.constraints = []
        self.objective = None
        self.fitness = None

    @staticmethod
    def domains_to_genes(domains=DOMAINS):
        genes = [
            random.uniform(domains[index][0], domains[index][1])
            for index in range(CHROMOSOME_SIZE)
        ]
        return genes

    @staticmethod
    def genes_to_points(genes):
        return chunker(genes, 2)

    @staticmethod
    def points_to_genes(points):
        return [gen for genes in points for gen in genes]

    def __repr__(self):
        agent = {
            "genes": [],
            "constraints": self.constraints,
            "objective": self.objective,
            "fitness": self.fitness,
        }
        return beautifier(agent)


def remove_unnecessary_files():
    """Delete unused files. Return nothing"""
    for type in CONS["UNUSED_FILES"]:
        for file in glob.glob("*" + type):
            try:
                os.remove(file)
            except Exception:
                pass


def beautifier(something):
    """Place an object and it will return a beautiful easy-to-read string."""
    return json.dumps(something, default=lambda x: x.__dict__, indent=2)


def chunker(seq, size):
    """Split a list into equal segments (maybe except the last one)."""
    return list(seq[pos : pos + size] for pos in range(0, len(seq), size))


def clear_line(number_of_lines=1):
    CURSOR_UP_ONE = "\x1b[1A"
    ERASE_LINE = "\x1b[2K"
    for _ in range(number_of_lines):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


def logging():
    """Log current data to a file"""

    global data

    object_to_dump = [CONSTANTS, data]
    with open(CONS["OUTPUT_FILE"], "w") as file:
        json.dump(object_to_dump, file, default=lambda x: x.__dict__, indent=2)


def is_data_match():
    """Check if previous data is suitable to join with current data."""

    with open(CONS["OUTPUT_FILE"], "r") as file:
        old_constants = json.load(file)[0]
    if old_constants == CONSTANTS:
        return True
    return False


def loading():
    """Join previous data to current data."""

    global data
    global population

    with open(CONS["OUTPUT_FILE"], "r") as file:
        old_data = json.load(file)[1]

    for old_population in old_data:
        population = [Chromosome() for _ in range(len(old_population))]
        for chromosome, old_chromosome in zip(population, old_population):
            chromosome.genes = old_chromosome["genes"]
            chromosome.constraints = old_chromosome["constraints"]
            chromosome.objective = old_chromosome["objective"]
            chromosome.fitness = old_chromosome["fitness"]
        data.append(population)


def need_initialize():
    """Check if population initialization is needed."""

    if CONS["IS_LOADING"] and os.path.exists(CONS["OUTPUT_FILE"]):
        if is_data_match():
            print("Old data is valid. Reuse")
            answer = False
            loading()
        else:
            print("Old data is not match. Overwrite.")
            answer = True
    else:
        print("Old data is not found. Initialize new data.")
        answer = True
    # time.sleep(1)
    clear_line()
    return answer


def call(genes):
    """Put in a list of coordinates that will be converted to list of points
    and be sent to kernel.py. Finally return a dict of results."""

    points = Chromosome.genes_to_points(genes)
    output = subprocess.check_output(
        "py test/virtualkernel.py -- %s" % (points),
        # "abaqus cae noGUI=sub/kernel.py -- %s" % (points),
        shell=True,
        universal_newlines=True,
    )
    return ast.literal_eval(output)


def penalty(genes):
    """Calculate constraints from given expressions."""

    constraints = []
    points = Chromosome.genes_to_points(genes)
    for index, [x_coordinate, y_coordinate] in enumerate(points):
        # TODO: Globalizing all genes may make memory exhausted, need to change
        globals()["x" + str(index)] = x_coordinate
        globals()["y" + str(index)] = y_coordinate
    # globals()["p"] = polygon_perimeter(genes)

    for expressions in CONSTRAINTS:
        if eval(expressions):
            constraints.append(0)
        else:
            for operator in CONS["OPERATORS"]:
                if operator in expressions:
                    splited_exp = [
                        eval(element)  # TODO: Security breach, need to fix
                        for element in expressions.split(operator)
                    ]
                    break
            constraints.append(abs(splited_exp[0] - splited_exp[1]) + 1)
    return constraints


def singletask():
    """Run requests one by one. Slower but safer."""

    global population
    for order, chromosome in enumerate(population):
        result = call(chromosome.genes)
        chromosome.objective = result["objective"]
        chromosome.constraints = penalty(chromosome.genes)  # TODO: Temporary
        # print(result)
        print(
            "Done with chromosome %s, generation %s." % (order + 1, len(data))
        )
        clear_line()


def multitask():
    """Run requests concurrently. Faster but more risky."""

    global population
    input = [chromosome.genes for chromosome in population]
    items = chunker(input, CONS["CORE_SIZE"])
    results = []
    for order, item in enumerate(items):
        big_bool = 0
        while True:
            small_bool = True
            temp = []
            try:
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    output = executor.map(call, item)
                    for index, result in enumerate(output):
                        # print(index, result)
                        temp.append(result)
            except Exception:
                small_bool = False
                big_bool += 1
            if small_bool:
                results.extend(temp)

                print(COLORS["WARNING"], end="")
                print("COMPLETED:")
                print(COLORS["ENDC"], end="")

                print(
                    f"  "
                    f"{'Generation:':<15}"
                    f"{len(data) + 1:03}"
                    f"{'/'}{CONS['GENERATION_SIZE']:03}"
                )
                print(
                    f"  "
                    f"{'Chromosome:':<15}"
                    f"{order * CONS['CORE_SIZE'] + len(item):03}"
                    f"{'/'}{CONS['POPULATION_SIZE']:03}"
                )

                clear_line(3)
                break
            if big_bool == CONS["RETRY_COUNT"]:
                print("Failed too many times")
                print(item)
                exit()
    for chromosome, result in zip(population, results):
        chromosome.objective = result["objective"]
        chromosome.constraints = penalty(chromosome.genes)  # TODO: Temporary


def self_recover():
    print(COLORS["WARNING"], end="")
    print("TAKING A BREAK")
    print(COLORS["ENDC"], end="")

    print("Sleep", CONS["TIME_SLEEP"], "second to finish all processes...")
    time.sleep(CONS["TIME_SLEEP"])
    clear_line()

    print("Removing all unused files...")
    remove_unnecessary_files()
    time.sleep(1)
    clear_line()

    print("Continue...")

    # time.sleep(1)
    clear_line(2)


def initialization():
    global population
    population = [Chromosome() for _ in range(CONS["POPULATION_SIZE"])]


def fitness():
    global data
    global population

    # Calculate objectives and constraints of all chromosomes
    if CONS["CALCULATE_MODE"] == "MULTITASK":
        multitask()
    elif CONS["CALCULATE_MODE"] == "SINGLETASK":
        singletask()
    else:
        print("Invalid calculation mode")
        exit()

    # Find the minimum objective of valid chromosomes
    valid_chromosomes = []
    for chromosome in population:
        if all(x == 0 for x in chromosome.constraints):
            valid_chromosomes.append(chromosome.objective)
    min_objective = min(valid_chromosomes) if valid_chromosomes else 0

    # Calculate every fitnesses
    for chromosome in population:
        chromosome.fitness = chromosome.objective - CONS["AMP_FACT"] * abs(
            chromosome.objective - min_objective
        ) * sum(chromosome.constraints)

    # Ranking
    max_fitness = max([chromosome.fitness for chromosome in population])
    min_fitness = min([chromosome.fitness for chromosome in population])
    for chromosome in population:
        chromosome.fitness = (
            (chromosome.fitness - min_fitness)
            / (max_fitness - min_fitness)
            * 100
        )
    population = sorted(
        population, key=lambda chromosome: chromosome.fitness, reverse=True
    )

    # Add that generation to data
    copied_population = copy.deepcopy(population)
    data.append(copied_population)
    # print("Done with generation", len(data))

    # Logging if needed
    if CONS["IS_LOGGING"]:
        logging()


def selection():
    global population
    population = population[: int(CONS["SELECTION_RATE"] * len(population))]


def crossover():
    global population
    children = []

    for _ in range(CONS["POPULATION_SIZE"] - len(population)):
        child = Chromosome()
        # Select parents based on their fitnesses
        [parent_1, parent_2] = random.choices(
            population=population,
            weights=[chromosome.fitness for chromosome in population],
            k=2,
        )
        # Select genes of parent_1 based on its fitness
        genes_of_parent_1 = random.sample(
            population=range(CHROMOSOME_SIZE),
            k=int(
                CHROMOSOME_SIZE
                * (parent_1.fitness / (parent_1.fitness + parent_2.fitness))
            ),
        )
        # Merge genes
        for gen in range(CHROMOSOME_SIZE):
            if gen in genes_of_parent_1:
                child.genes[gen] = parent_1.genes[gen]
            else:
                child.genes[gen] = parent_2.genes[gen]
        children.append(child)

    population.extend(children)


def mutation():
    global population

    if CONS["MUTATION_MODE"] == "UNION":
        # Major mutation
        major_indexes = random.sample(
            population=range(CONS["POPULATION_SIZE"]),
            k=int(CONS["MAJOR_MUTATION_RATE"] * CONS["POPULATION_SIZE"]),
        )
        for major_index in major_indexes:
            population[major_index].genes = Chromosome.domains_to_genes()
        # Minor mutation
        for chromosome in population:
            minor_indexes = random.sample(
                population=range(CHROMOSOME_SIZE),
                k=int(CONS["MINOR_MUTATION_RATE"] * CHROMOSOME_SIZE),
            )
            for minor_index in minor_indexes:
                chromosome.genes[minor_index] = random.uniform(
                    DOMAINS[minor_index][0], DOMAINS[minor_index][1]
                )

    elif CONS["MUTATION_MODE"] == "INTERSECT":
        major_indexes = random.sample(
            population=range(CONS["POPULATION_SIZE"]),
            k=int(CONS["MAJOR_MUTATION_RATE"] * CONS["POPULATION_SIZE"]),
        )
        for major_index in major_indexes:
            minor_indexes = random.sample(
                population=range(CHROMOSOME_SIZE),
                k=int(CONS["MINOR_MUTATION_RATE"] * CHROMOSOME_SIZE),
            )
            for minor_index in minor_indexes:
                population[major_index].genes[minor_index] = random.uniform(
                    DOMAINS[minor_index][0], DOMAINS[minor_index][1]
                )

    else:
        print("Invalid mutation mode")
        exit()


def genetic_algorithm():
    global data
    global population

    data = []
    population = []

    if need_initialize():
        initialization()
        fitness()

    while len(data) < CONS["GENERATION_SIZE"]:
        selection()
        crossover()
        mutation()
        fitness()

        if len(data) % CONS["REST_PERIOR"] == 0:
            self_recover()

    objectives = [population[0].objective for population in data]
    objective = max(objectives)
    index = objectives.index(objective)
    genes = data[index][0].genes
    constraints = data[index][0].constraints

    return index, objective, genes, constraints


if __name__ == "__main__":
    import timeit

    start = timeit.default_timer()
    index, objective, genes, constraints = genetic_algorithm()
    stop = timeit.default_timer()

    print(COLORS["WARNING"] + "RESULT:" + COLORS["ENDC"])
    # print(COLORS["OKBLUE"], end="")
    print(f"{'  Maximum objective:':<20}{objective:>12.3f}")
    print(f"{'  Its index:':<20}{index:>12}")
    print(f"{'  Its constraints:':<20}{str(constraints):>12}")
    print(f"{'  Running time:':<20}{(stop - start):>12.2f}")
    # print("Its genes:")
    # print(beautifier(genes))
    # print(COLORS["ENDC"], end="")

    values = [population[0].objective for population in data]
    plot.main(values, is_animation=False)
