import pandas as pd
from source import WallFooting, ColumnFooting
import math

df = pd.read_csv("input/example1.csv")
print(df.head())

for index, row in df.iterrows():

    ftng_type = row["ftng_type"]
    width = row["width"]
    d_l = row["dead_load"]
    l_l = row["live_load"]
    f_c = row["f_c"]
    grade = row["grade"]
    a_s_p = row["a_s_p"]
    w_c = 150 if math.isnan(row["w_c"]) else row["w_c"]
    w_e = 100 if math.isnan(row["w_e"]) else row["w_e"]
    bottom = 4 if math.isnan(row["bottom_of_ftng"]) else row["bottom_of_ftng"]
    precision = 0.5 if math.isnan(row["precision"]) else row["precision"]
    bar_coat = (
        None
        if type(row["bar_coat"]) is float and math.isnan(row["bar_coat"])
        else row["bar_coat"]
    )
    conc_type = (
        "nw"
        if type(row["conc_type"]) is float and math.isnan(row["conc_type"])
        else row["conc_type"]
    )

    if ftng_type == "wall":
        wall_type = row["wall_type"]
        wall_width = width

        footing = WallFooting(
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
        max_width = (
            None if math.isnan(row["width_restriction"]) else row["width_restriction"]
        )
        col_loc = (
            "center"
            if type(row["col_loc"]) is float and math.isnan(row["col_loc"])
            else row["col_loc"]
        )
        col_width = width

        footing = ColumnFooting(
            precision,
            col_width,
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
