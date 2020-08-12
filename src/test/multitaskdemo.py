"""This uses concurrent tasks to run abaqus requests.
Requests are split into smaller segments based on computer cores and then
send them to abaqus by using subprocess, which is avoid reading some files
at the same time and lead to collapse.
"""
import timeit
import random
import subprocess
import concurrent.futures
import inputprocess

POPULATION_SIZE = 50
CORE_SIZE = 4
domain = inputprocess.create_domains_list()
chromosome_size = len(domain)


def chunker(seq, size):
    return list(seq[pos : pos + size] for pos in range(0, len(seq), size))


def call(value):
    output = subprocess.check_output(
        "abaqus cae noGUI=kernel.py -- %s" % (value),
        shell=True,
        universal_newlines=True,
    )
    return float(output)


def chromosome():
    list = []
    for index in range(chromosome_size):
        list.append(random.uniform(domain[index][0], domain[index][1]))
    return list


def singletask(input):
    results = []
    for order, item in enumerate(input):
        result = call(item)
        results.append(result)
        print(result)
        print("Done with item", order)
    return (len(results) == len(input))


def multitask(input):
    items = chunker(input, CORE_SIZE)
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
                        print(result)
                        temp.append(result)
            except Exception:
                small_bool = False
                big_bool += 1
            if small_bool:
                results.extend(temp)
                print("Done with item", order * CORE_SIZE + len(item) - 1)
                break
            if big_bool == 5:
                print("Failed too many times")
                print(item)
                exit()
    return (len(results) == len(input))


if __name__ == "__main__":
    input = [chromosome() for _ in range(POPULATION_SIZE)]

    start = timeit.default_timer()
    # print(singletask(input))
    print(multitask(input))
    stop = timeit.default_timer()

    print("Time: %.2f" % (stop - start))
