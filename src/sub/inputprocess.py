import json
import re
from sub.translate import translate_data
from sub.translate import INPUT_FILE

# Read data in profile.csv and write to input.json
translate_data()

with open(INPUT_FILE) as file:
    string = "\n".join(file.read().splitlines())
    result = json.loads(
        re.sub(r"(^|\s+)//.*$", "", string, flags=re.MULTILINE)
    )

# Public variables
for key, value in result.items():
    globals()[key] = value


if __name__ == "__main__":
    print("DOMAINS")
    print(json.dumps(globals()["DOMAINS"], indent=4))

    print("RULES")
    print(json.dumps(globals()["RULES"], indent=4))

    print("CONSTRAINTS")
    print(json.dumps(globals()["CONSTRAINTS"], indent=4))

    print("CONSTANTS")
    print(json.dumps(globals()["CONSTANTS"], indent=4))
