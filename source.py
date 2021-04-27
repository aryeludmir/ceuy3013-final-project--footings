import math


class Footing:
    def __init__(
        self,
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
    ):
        self.d_l = d_l
        self.l_l = l_l
        self.f_c = f_c
        self.f_y = f_y
        self.a_s_p = a_s_p
        self.bottom = bottom
        self.bar_coat = bar_coat
        self.conc_type = conc_type
        self.w_c = w_c
        self.w_e = w_e

    def factor_loads(self, d_l, d_d):
        """Calculates the minimum design load by multiplying service loads by given factors (ACI Section 5.3.1)
        NOTE: This ACI section is slightly modified for our purpose. See ACI Code, Section 5.3 for more details.
        """

        return (1.6 * d_l) + (1.2 * d_d)

    def reqd_area(self, rho, b, d):
        """Calculates the minimum flexural reinforcement required by analysis (ACI Section 9.6.1.1)

        rho = ratio of tension steel area to effective concrete area
        b = section width
        d = effective depth of steel
        """

        return rho * b * d

    def min_area_beams(self, concrete_strength, steel_strength, b, d):
        """Calculates the minimum flexural reinforcement for nonprestressed beams
        as required by ACI Section 9.6.1.2
        """
        a = (3 * math.sqrt(concrete_strength) / steel_strength) * b * d
        b = (200 / steel_strength) * b * d
        result = max(a, b)

        print(
            "ACI Section 9.6.1.2 - Minimum flexural reinforcement for nonprestressed beams: ",
            result,
        )

        return result

    def net_asp(self, asp, w_e, w_c, h, bottom):
        return asp - (w_e * (bottom - h)) - (w_c * h)


class WallFooting(Footing):
    def __init__(
        self,
        width,
        wall_type,
        d_l,
        l_l,
        f_c,
        f_y,
        a_s_p,
        bottom,
        bar_coat=None,
        conc_type="nw",
        w_c=150,
        w_e=100,
    ):
        pass
        #super.__init__()

    def design_wall_footing():
        pass


class ColumnFooting(Footing):
    def __init__(
        self,
        width,
        d_l,
        l_l,
        f_c,
        f_y,
        a_s_p,
        bottom,
        width_restriction=None,
        bar_coat=None,
        col_loc="center",
        conc_type="nw",
        w_c=150,
        w_e=100,
    ):
        pass
        #super.__init__()

    def design_column_footing():
        pass
