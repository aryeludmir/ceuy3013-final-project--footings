import json
from source import WallFooting, ColumnFooting
import math

results_list = []

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
    bar_coat = i["bar_coat"]
    w_c = i["w_c"] if i["w_c"] else 150
    w_e = i["w_e"] if i["w_e"] else 100
    bottom = i["bottom_of_ftng"] if i["bottom_of_ftng"] else 4
    precision = i["precision"] if i["precision"] else 0.08333333333
    conc_type = i["conc_type"] if i["conc_type"] else "nw"

    log = open(f"output/{name}.txt", "w")

    if ftng_type == "wall":
        wall_type = i["wall_type"]
        wall_width = i["width"]

        footing = WallFooting(
            name,
            log,
            precision,
            wall_width,
            wall_type,
            d_l,
            l_l,
            f_c,
            grade,
            a_s_p,
            bottom,
            bar_coat,
            conc_type,
            w_c,
            w_e,
        )

    else:
        max_width = i["width_restriction"]
        col_loc = i["col_loc"] if i["col_loc"] else "interior"
        col_width = i["width"]
        col_length = i["length"]

        footing = ColumnFooting(
            name,
            log,
            precision,
            col_width,
            col_length,
            d_l,
            l_l,
            f_c,
            grade,
            a_s_p,
            bottom,
            max_width,
            bar_coat,
            col_loc,
            conc_type,
            w_c,
            w_e,
        )

    print(footing)

    results_list.append(footing.get_ftng_dict())

with open("output/output.json", "w") as outfile:
    json.dump(results_list, outfile, indent=4)
