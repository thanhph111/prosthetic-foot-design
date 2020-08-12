"""This script file is used to read points data from .csv file
and write to input .txt file.
"""

import csv
from sub.inputprocess import CSV_FILE
from sub.inputprocess import INPUT_FILE


def _create_domains():
    """Read points data from .csv file. Return 2-dim array."""

    domains = []

    csv_file = open(CSV_FILE)
    reader = csv.DictReader(csv_file)

    # Transform every lines to meet right format
    for row in reader:
        if row["Angle"] == "0":  # It means that row is horizontal
            start_x = float(row["Start X"])
            end_x = float(row["End X"])
            domain = ["x", int(row["Hyperlink"])]
            domain.extend(sorted([start_x, end_x]))
        else:
            start_y = float(row["Start Y"])
            end_y = float(row["End Y"])
            domain = ["y", int(row["Hyperlink"])]
            domain.extend(sorted([start_y, end_y]))
        domains.append(domain)

    csv_file.close()

    # Sort the table by primary key (order) and then by secondary key (x/y)
    domains.sort(key=lambda x: (x[1], x[0]), reverse=False)

    # Join every lines in table to strings
    for index, value in enumerate(domains):
        domains[index] = " ".join(
            [value[0] + str(value[1]), str(value[2]), str(value[3])]
        )

    return domains


def write_to_file(list):
    """Write the read table to input .txt file. No return."""

    with open(INPUT_FILE) as file:
        input_lines = file.read().splitlines()
    points_pos = input_lines.index("*POINTS")
    rules_pos = input_lines.index("*RULES")

    # Delete the previous data
    del input_lines[(points_pos + 1) : rules_pos]
    # Insert new data
    list.append("")
    input_lines[(points_pos + 1) : (points_pos + 1)] = list

    # Rewrite to the same input file
    with open(INPUT_FILE, "w") as file:
        file.writelines("\n".join(input_lines))


if __name__ == "__main__":
    write_to_file(_create_domains())
