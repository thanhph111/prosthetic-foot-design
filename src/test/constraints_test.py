import ga
import sub.plot
from sub.inputprocess import CONSTANTS as CONS
from sub.inputprocess import CONSTRAINTS

data = sub.plot.get_data()
chromosome = data[119][0]
genes = chromosome["genes"]
points = ga.Chromosome.genes_to_points(genes)
result = chromosome["result"]

for index, [x_coordinate, y_coordinate] in enumerate(points):
    globals()["x" + str(index)] = x_coordinate
    globals()["y" + str(index)] = y_coordinate
globals()["f"] = result["field_output"]
globals()["sigma"] = CONS["SIGMA"]

for expressions in CONSTRAINTS:
    for operator in CONS["OPERATORS"]:
        if operator in expressions:
            splited_exp = [
                eval(element) for element in expressions.split(operator)
            ]
            break
    print(splited_exp)
