"""This script is used to read data from input.txt file,
translate user readable data to kernel processable data.
Import it and all constants can be accessable in script.
"""

import ast

# import translate

FILE = "../data/input.txt"

with open(FILE) as file:
    input = file.read().splitlines()
    input = [row for row in input if row and not row.startswith("#")]

# Find the positions of points, rules and constants data
points_pos = input.index("*POINTS")
rules_pos = input.index("*RULES")
constraints_pos = input.index("*CONSTRAINTS")
constants_pos = input.index("*CONSTANTS")


def create_domains():
    """Create points data table. Return 2-dim array"""
    domains = []
    for row in input[points_pos + 1 : rules_pos]:
        domain = [float(segments) for segments in row.split(" ")[1:3]]
        domains.append(domain)
    return domains


def create_rules():
    """Create a dictionary containing lines & arcs rules.
    Return dictionary with string keys and list of integer values.
    """

    rules = {}
    rules["Lines"] = []
    rules["Arcs"] = []
    lines_pos = input.index("**Lines")
    arcs_pos = input.index("**Arcs")

    for row in input[lines_pos + 1 : arcs_pos]:
        segments = list(map(int, row.split(" ")))
        rules["Lines"].append(segments)

    for row in input[arcs_pos + 1 : constraints_pos]:
        segments = list(map(int, row.split(" ")))
        rules["Arcs"].append(segments)
    return rules


def create_constraints():
    """Create a list of constraint expressions.
    Return a list of string.
    """

    constraints = input[constraints_pos + 1 : constants_pos]
    return constraints


def _create_constants():
    """Create a dictionary containing contants name and their value.
    Return dictionary with string keys and float values.
    """

    constants = {}
    for row in input[constants_pos + 1 :]:
        # TODO: Use exec() instead
        segments = row.split(" = ", 1)
        try:
            constants[segments[0]] = ast.literal_eval(segments[1])
        except ValueError:
            constants[segments[0]] = segments[1]
    return constants


# Globalize all processed variables
# Modules importing this module are able to access all global variables
constants = _create_constants()
for var, value in constants.items():
    globals()[var] = value

if __name__ == "__main__":
    _create_constants()
    print("Domains")
    print(create_domains())
    print("Rules")
    print(create_rules())
    print("Constraints")
    print(create_constraints())
    print("Constants")
    print(constants)
