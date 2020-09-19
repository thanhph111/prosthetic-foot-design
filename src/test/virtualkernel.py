import sys
import ast
import random


def points_to_genes(points):
    return [gen for genes in points for gen in genes]


def virtual_calculate(coordinates):
    return {
        "objective": random.uniform(0.5, 8),
        "field_output": random.uniform(3, 7) * 10,
    }


if __name__ == "__main__":
    system_argument_list = sys.argv[2:]
    # print(system_argument_list)
    if system_argument_list:
        try:
            points = ast.literal_eval("".join(system_argument_list))
        except SyntaxError:
            points = ast.literal_eval(",".join(system_argument_list))
    else:
        points = [
            [114.40712390296207, 154.4548506587745],
            [155.83216298727956, 153.69293386572238],
            [158.73231133486775, 131.575630521931],
            [100.39661174612677, 97.96224914262834],
            [133.59506590428762, 34.38834774229362],
            [317.4845802401193, 28.45614216554591],
            [323.72203751729865, 11.091371502325634],
            [58.67622185352986, 10.24172336521795],
            [68.69993077132263, 29.048814235453474],
            [108.70961349716724, 32.43813789262146],
            [83.1338504234908, 71.65940041608457],
            [116.8888742298014, 135.3959448675419],
        ]
    print(virtual_calculate(points_to_genes(points)))
