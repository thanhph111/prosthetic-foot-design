import ga
import concurrent.futures
import timeit
import subprocess
import ast
import matplotlib as maplot
import matplotlib.pyplot as pyplot

SIZE = 100
CORE_SIZE = 3
RETRY_COUNT = 15
SAMP_RATE = CORE_SIZE


def call(genes):
    points = ga.Chromosome.genes_to_points(genes)
    output = subprocess.check_output(
        "py test/virtualkernel.py -- %s" % (points),
        # "abaqus cae noGUI=sub/kernel.py -- %s" % (points),
        shell=True,
        universal_newlines=True,
    )
    return ast.literal_eval(output)


def singletask():
    start = timeit.default_timer()
    global population
    time_axis = [0]

    for order, chromosome in enumerate(population):
        call(chromosome.genes)
        if (order + 1) % SAMP_RATE == 0:
            stop = timeit.default_timer()
            time_axis.append(stop - start)
    return time_axis


def multitask():
    start = timeit.default_timer()
    global population
    time_axis = [0]

    input = [chromosome.genes for chromosome in population]
    items = ga.chunker(input, CORE_SIZE)
    for order, item in enumerate(items):
        big_bool = 0
        while True:
            small_bool = True
            try:
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    executor.map(call, item)
            except Exception:
                small_bool = False
                big_bool += 1
            if small_bool:
                stop = timeit.default_timer()
                time_axis.append(stop - start)
                break
            if big_bool == RETRY_COUNT:
                print("Failed too many times")
                print(item)
                exit()
    return time_axis


# def write():
#     global population
#
#     count_axis = list(range(0, SIZE + SAMP_RATE, SAMP_RATE))
#     time_axis = [0]
#     for size in count_axis[1:]:
#         population = [ga.Chromosome() for _ in range(size)]
#
#         start = timeit.default_timer()
#         singletask()
#         stop = timeit.default_timer()
#         time_axis.append(stop - start)
#
#     with open("plot", "w") as file:
#         file.write(str(count_axis) + "\n")
#         file.write(str(time_axis) + "\n")


def write():
    global population

    population = [ga.Chromosome() for _ in range(SIZE)]
    count_axis = list(range(0, SIZE + SAMP_RATE, SAMP_RATE))
    time_axis = singletask()

    with open("plot", "a") as file:
        file.write(str(count_axis) + "\n")
        file.write(str(time_axis) + "\n")


def read():
    with open("plot", "r") as file:
        lines = file.read().splitlines()
        count_axis_1 = ast.literal_eval(lines[0])
        time_axis_1 = ast.literal_eval(lines[1])
        count_axis_2 = ast.literal_eval(lines[2])
        time_axis_2 = ast.literal_eval(lines[3])

    print(
        len(count_axis_1),
        len(time_axis_1),
        len(count_axis_2),
        len(time_axis_2),
    )

    maplot.rcParams["toolbar"] = "None"

    fig = pyplot.figure(figsize=(12, 5))

    subplot = fig.add_subplot(111, frameon=True)
    subplot.spines["right"].set_visible(False)
    subplot.spines["left"].set_visible(False)
    subplot.spines["top"].set_visible(False)

    subplot.plot(count_axis_1[:-1], time_axis_1[:-1], marker="o")
    subplot.plot(count_axis_2[:-1], time_axis_2, marker="o")

    # pyplot.show()
    fig.savefig(
        "plot.svg",
        transparent=True,
        dpi=300,
    )


if __name__ == "__main__":
    # write()
    read()
