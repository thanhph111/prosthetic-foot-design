"""This script file is used to read points data from .csv file
and write to input .txt file.
"""

import csv
import json
import re


CSV_FILE = "../data/profile.csv"
INPUT_FILE = "../data/input.json"


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

    return [[domain[2], domain[3]] for domain in domains]


def translate_data(new_domains=_create_domains()):
    """Write the read table to input .txt file. No return."""

    with open(INPUT_FILE) as file:
        input = file.read().splitlines()

    with open(INPUT_FILE) as file:
        string = file.read()
        # Remove comment lines
        string = re.sub(r"(^|\s+)//.*$", "", string, flags=re.MULTILINE)
        old_domains = json.loads(string)["DOMAINS"]

    # Check if old domain same size with the new one
    if len(old_domains) != len(new_domains) or any(
        len(x) != 2 for x in old_domains
    ):
        print("Old data structure is not match the new ones.")
        exit()
    else:
        # Flatten lists
        old_values = [item for elem in old_domains for item in elem]
        new_values = [item for elem in new_domains for item in elem]
        # Replace old values with new one in each line if match
        index = 0
        line = 0
        while index < len(old_values) and line < len(input):
            if re.match(rf"\s+{str(old_values[index])}", input[line]):
                input[line] = input[line].replace(
                    str(old_values[index]), str(new_values[index]), 1
                )
                index += 1
            line += 1

    # Rewrite to the same input file
    with open(INPUT_FILE, "w") as file:
        file.writelines("\n".join(input))


if __name__ == "__main__":
    translate_data()
