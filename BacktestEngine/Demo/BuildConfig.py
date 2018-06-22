import os
from itertools import product
import json

Parameters = {

    # Model parameters
    "frequency": [5, 10, 15],
    "offset": [0, 1, 2, 3, 4],
    "tca": [-1]

    ##  Add other parameters below as a dict element. ##

    # The key string should match the members in config.py
    # The values should be lists

}

# --------------------------------------------------------------- #

try:
    os.mkdir("./Config_files")
except FileExistsError:
    pass


for idx, paras in enumerate(product(*Parameters.values())):
    current_dict = {}
    for key, value in zip(Parameters.keys(), paras):
        current_dict[key] = value
    with open("./Config_files/config_{}.json".format(idx), "w") as f:
        json.dump(current_dict, f, indent=4)