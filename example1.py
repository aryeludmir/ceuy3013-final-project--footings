import pandas as pd
from source import WallFooting, ColumnFooting

df = pd.read_csv("example1.csv")
print(df.head())

for index, row in df.iterrows():

    ftng_type = row["ftng_type"]
    width = row["width"]
    d_l = row["dead_load"]
    l_l = row["live_load"]
    conc_type = row["conc_type"]
    w_c = row["w_c"]
    w_e = row["w_e"]
    f_c = row["f_c"]
    f_y = row["f_y"]
    a_s_p = row["a_s_p"]
    bottom = row["bottom_of_ftng"]
    bar_coat = row["bar_coat"]
    precision = row["precision"]

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
            f_y,
            a_s_p,
            bottom,
            bar_coat,
            conc_type,
            w_c,
            w_e,
        )

    else:
        max_width = row["width_restriction"]
        col_loc = row["col_loc"]

        footing = ColumnFooting(
            precision,
            width,
            d_l,
            l_l,
            f_c,
            f_y,
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
