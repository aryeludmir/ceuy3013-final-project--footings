# This file is meant as a python script.
# To run it, simply type `python ex1.py`

import json
from source import WallFooting, ColumnFooting
import math

# instantiate the list to hold program outputs
results_list = [] 

# open and load json file that contains footing design criteria
with open("input/ex1.json") as json_file:
    data = json.load(json_file)

for i in data:

    name = i["id"]
    ftng_type = i["ftng_type"]
    d_l = i["dead_load"]
    l_l = i["live_load"]
    f_c = i["f_c"]
    grade = i["grade"]
    a_s_p = i["a_s_p"]
    w_c = i["w_c"] if i["w_c"] else 150
    w_e = i["w_e"] if i["w_e"] else 100
    bottom = i["bottom_of_ftng"] if i["bottom_of_ftng"] else 4
    precision = i["precision"] if i["precision"] else 0.08333333333
    conc_type = i["conc_type"] if i["conc_type"] else "nw"

    # verbose output to this text file 
    log = open(f"output/{name}.txt", "w")
    log.write(f"Footing Design for {name}\n\n")

    # create a wall footing...
    if ftng_type == "wall":
        wall_type = i["wall_type"]
        wall_width = i["width"]
        footing = WallFooting(name, log, precision, wall_width, wall_type,
                              d_l, l_l, f_c, grade, a_s_p, bottom, conc_type, w_c, w_e)
    # or a column footing...
    else:
        max_width = i["width_restriction"]
        col_loc = i["col_loc"] if i["col_loc"] else "interior"
        col_width = i["width"]
        footing = ColumnFooting(name, log, precision, col_width, d_l, l_l, f_c,
                                grade, a_s_p, bottom, max_width, col_loc, conc_type, w_c, w_e)

    # print short results on screen for convenience
    print(footing)
    
    # append result to list...
    results_list.append(footing.ftng_dict())
    
# ...add list to final output json file
with open("output/output.json", "w") as outfile:
    json.dump(results_list, outfile, indent=4)
