import math


class Footing:
    def factor_loads(self, d_l, l_l):
        """Calculates the minimum design load by multiplying service loads by given factors (ACI Section 5.3.1).
        For columns the result is in kips, and for walls the result is in kip/ft.
        NOTE: This ACI section is slightly modified for our purpose. See ACI Code, Section 5.3 for more details.
        """
        return (1.2 * d_l) + (1.6 * l_l)

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
        """Returns the net allowable soil pressure in ksf"""
        return (asp - (w_e * (bottom - h)) - (w_c * h)) / 1000

    def round_to_upper(self, x, precision=0.5):
        """ """
        ceil = math.ceil(x)

        while (ceil - x) > precision:
            ceil -= precision
        return ceil

    def factored_soil_pressure(slef, P, dimension):
        """ """
        return P / dimension

    def find_d(self, h, ftng_type, bar_size=8):
        """ """
        if ftng_type == "wall":
            return (h * 12) - 3 - ((bar_size / 8) / 2)
        else:
            return (h * 12) - 3 - (bar_size / 8)

    def find_lam(self, conc_type):
        """ """
        if conc_type == "nw":
            return 1
        elif conc_type == "lw":
            return 0.75
        elif conc_type == "s_lw":
            return 0.85


class WallFooting(Footing):
    def __init__(
        self,
        precision,
        wall_width,
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
        self.h = 1.5  # ft
        self.d = self.find_d(self.h, "wall")  # in

        self.design_wall_footing(
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

    def design_wall_footing(
        self,
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
    ):

        load = d_l + l_l  # k/ft
        factored_load = self.factor_loads(d_l, l_l)  # k/ft
        net_asp = self.net_asp(a_s_p, w_e, w_c, self.h, bottom)  # ksf
        req_width = self.find_req_width(load, net_asp, precision)  # ft
        q_u = self.factored_soil_pressure(factored_load, req_width)  # ksf
        check_shear = self.check_one_way_shear(
            q_u, self.d, req_width, wall_width, f_c, conc_type
        )

    def find_req_width(self, load, net_asp, precision):
        """returns required width for wall footing, rounded up to the nearest inch."""
        return self.round_to_upper((load / net_asp), precision)

    def check_one_way_shear(self, q_u, d, req_width, wall_width, f_c, conc_type):
        """ """
        lam = self.find_lam(conc_type)

        v_u = q_u * 1 * (((req_width - (wall_width / 12)) / 2) - (d / 12))  # kip
        v_c = (2 * lam * math.sqrt(f_c) * 12 * d) / 1000  # kip
        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.find_d(self.h, "wall")
            v_u = q_u * 1 * (((req_width - (wall_width) / 12) / 2) - (new_d / 12))
            v_c = (2 * lam * math.sqrt(f_c) * 12 * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c
            self.d = new_d

        if phi_vn < v_u:
            self.d = self.round_to_upper(
                (v_u * 1000 / (2 * lam * 0.75 * math.sqrt(f_c) * 12))
            )  # in.
            self.h = self.d + 3 + ((8 / 8) / 2)
            v_c = (2 * lam * math.sqrt(f_c) * 12 * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c

        return phi_vn


class ColumnFooting(Footing):
    def __init__(
        self,
        precision,
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
        self.h = 2  # ft.
        self.d = self.find_d(self.h, "column")  # in

        self.design_column_footing(
            precision,
            width,
            d_l,
            l_l,
            f_c,
            f_y,
            a_s_p,
            bottom,
            width_restriction,
            bar_coat,
            col_loc,
            conc_type,
            w_c,
            w_e,
        )

    def design_column_footing(
        self,
        precision,
        width,
        d_l,
        l_l,
        f_c,
        f_y,
        a_s_p,
        bottom,
        width_restriction,
        bar_coat,
        col_loc,
        conc_type,
        w_c,
        w_e,
    ):
        load = d_l + l_l  # kip
        factored_load = self.factor_loads(d_l, l_l)  # kip
        net_asp = self.net_asp(a_s_p, w_e, w_c, self.h, bottom)  # ksf
        req_area = self.find_req_area(load, net_asp)  # sqft
        req_dims = self.find_req_dims(req_area, width_restriction, precision)  # ft
        actual_area = req_dims[0] * req_dims[1]  # sqft
        q_u = self.factored_soil_pressure(factored_load, actual_area)  # ksf
        two_way_shear = self.check_two_way_shear(
            q_u, actual_area, width, self.d, f_c, col_loc, conc_type
        )
        one_way_shear = self.check_one_way_shear(
            q_u, req_dims, width, self.d, f_c, conc_type
        )

    def find_req_area(self, load, net_asp):
        """returns required area for column footing rounded up to the nearest inch"""
        return load / net_asp

    def find_req_dims(self, area, max_width, precision):
        """returns footing dimensions"""

        if math.isnan(max_width):
            side = self.round_to_upper(math.sqrt(area), precision)
            return (side, side)
        else:
            long_side = self.round_to_upper((area / max_width), precision)
            return (max_width, long_side)

    def check_two_way_shear(self, q_u, area, width, d, f_c, col_loc, conc_type):
        """ """
        a = width + d  # in.
        b_0 = 4 * a  # in.
        v_u = q_u * (area - ((a / 12) ** 2))  # kip
        v_c = self.aci_sec22_6_5_2(d, b_0, f_c, conc_type, col_loc)  # kip
        phi_vn = 0.75 * v_c  # kip

        while phi_vn < v_u:
            self.h += 1 / 12
            new_d = self.find_d(self.h, "colmumn")
            new_a = width + new_d
            new_b_0 = 4 * a
            v_u = q_u * (area - ((new_a / 12) ** 2))
            v_c = self.aci_sec22_6_5_2(new_d, new_b_0, f_c, conc_type, col_loc) / 1000
            phi_vn = 0.75 * v_c
            self.d = new_d

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.find_d(self.h, "colmumn")
            new_a = width + new_d
            new_b_0 = 4 * a
            v_u = q_u * (area - ((new_a / 12) ** 2))
            v_c = self.aci_sec22_6_5_2(new_d, new_b_0, f_c, conc_type, col_loc) / 1000
            phi_vn = 0.75 * v_c
            self.d = new_d

        return phi_vn

    def aci_sec22_6_5_2(self, d, b_0, f_c, conc_type, col_loc):
        """ """

        lam = self.find_lam(conc_type)
        alpha_s = self.find_alpha_s(col_loc)

        v_ca = (4 * lam * math.sqrt(f_c) * b_0 * d) / 1000
        v_cb = (6 * lam * math.sqrt(f_c) * b_0 * d) / 1000
        v_cc = ((((alpha_s * d) / b_0) + 2) * lam * math.sqrt(f_c) * b_0 * d) / 1000

        return min(v_ca, v_cb, v_cc)

    def find_alpha_s(self, col_loc):
        """ """
        if col_loc == "interior":
            return 40
        elif col_loc == "edge":
            return 30
        elif col_loc == "corner":
            return 20

    def check_one_way_shear(self, q_u, dims, col_size, d, f_c, conc_type):
        """ """
        lam = self.find_lam(conc_type)
        v_u = q_u * dims[0] * ((dims[1] - (col_size / 12)) / 2 - (d / 12))  # kip
        v_c = (2 * lam * math.sqrt(f_c) * (dims[0] * 12) * d) / 1000  # kip

        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.find_d(self.h, "column")
            v_u = q_u * dims[0] * ((dims[1] - col_size) / (12 * 2) - (new_d / 12))
            v_c = (2 * lam * math.sqrt(f_c) * (dims[0] * 12) * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c
            self.d = new_d

        if phi_vn < v_u:
            self.d = self.round_to_upper(
                (v_u * 1000 / (2 * lam * 0.75 * math.sqrt(f_c) * dims[0] * 12))
            )  # in.
            self.h = self.d + 3 + (8 / 8)
            v_c = (2 * lam * math.sqrt(f_c) * (dims[0] * 12) * self.d) / 1000  # kip
            phi_vn = 0.75 * v_c

        return phi_vn

    # def get_func(name):
    #     """ """
    #     if name == "v_ca":
    #         return (4 * lam * math.sqrt(f_c) * b_0 * d) / 1000
    #     elif name == "v_cb":
    #         return (6 * lam * math.sqrt(f_c) * b_0 * d) / 1000
    #     elif name == "v_cc":
    #         return ((((alpha_s * d) / b_0) + 2) * lam * math.sqrt(f_c) * b_0 * d) / 1000
