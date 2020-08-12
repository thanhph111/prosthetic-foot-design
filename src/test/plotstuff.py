import json
import plot
from inputprocess import OUTPUT_FILE

# OUTPUT_FILE = (
#     "C:/Users/thanh/OneDrive/Current Projects/Flexure/src/GATest/output.json"
# )


def beautifier(something):
    """Place an object and it will return a beautiful easy-to-read string."""
    return json.dumps(something, default=lambda x: x.__dict__, indent=2)


def get_data():
    """Read output file to get data."""
    try:
        with open(OUTPUT_FILE, "r") as file:
            data = json.load(file)[1]
        return data
    except FileNotFoundError:
        print("Data file not found.")
        exit()


def get_values(data):
    """Get a list of all first chromosomes' objective values."""
    values = [population[0]["fitness"] for population in data]
    return values


def get_new_values(values):
    """Record any changes higher. Its size is the same as its argument's."""
    new_value = values[0]
    for index, value in enumerate(values):
        if value < new_value:
            print(index)


if __name__ == "__main__":
    # get_new_values(get_values(get_data()))
    things = [thing["fitness"] for thing in get_data()[2]]
    # for thing in things:
    #     thing["genes"] = 0

    plot.main(things)
    # things = get_data()[29][0]
    # print(beautifier(things))
