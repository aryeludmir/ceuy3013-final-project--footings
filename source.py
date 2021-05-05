import math


class Footing:
    def __init__(self, f_c, w_c, conc_type, grade):
        self.f_c = f_c
        self.w_c = w_c
        self.lam = self.get_lam(conc_type)
        self.beta_1 = self.get_beta_1(f_c)
        self.f_y, self.epsilon_y = self.get_steel_props(grade)

    def get_lam(self, conc_type):
        """ """
        if conc_type == "nw":
            return 1
        elif conc_type == "lw":
            return 0.75
        elif conc_type == "s_lw":
            return 0.85

    def get_beta_1(self, f_c):
        """ """
        if f_c > 4000:
            eq = 0.85 - (0.05 * (f_c - 4000) / 1000)
            return max(eq, 0.65)
        else:
            return 0.85

    def get_steel_props(slef, grade):
        """ """
        if grade == 40:
            return (40000, 0.00138)
        elif grade == 60:
            return (60000, 0.00207)
        elif grade == 75:
            return (75000, 0.00259)

    def get_d(self, h, ftng_type, bar_size=8):
        """ """
        if ftng_type == "wall":
            return (h * 12) - 3 - ((bar_size / 8) / 2)
        else:
            return (h * 12) - 3 - (bar_size / 8)

    def factor_loads(self, d_l, l_l):
        """Calculates the minimum design load by multiplying service loads by given factors (ACI Section 5.3.1).
        For columns the result is in kips, and for walls the result is in kip/ft.
        NOTE: This ACI section is slightly modified for our purpose. See ACI Code, Section 5.3 for more details.
        """
        return (1.2 * d_l) + (1.6 * l_l)

    def net_asp(self, asp, w_e, h, bottom):
        """Returns the net allowable soil pressure in ksf"""
        return (asp - (w_e * (bottom - h)) - (self.w_c * h)) / 1000

    def round_to_upper(self, x, precision=0.5):
        """ """
        ceil = math.ceil(x)
        temp1 = ceil
        temp2 = ceil

        if (temp1 - x) > 0.5:
            temp1 -= 0.5

        while (temp2 - x) > precision:
            temp2 -= precision

        return min(temp1, temp2)

    def round(self, x, n):
        """ """
        x = x * 10 ** n
        ceil = math.ceil(x)
        return ceil / (10 ** n)

    def factored_soil_pressure(self, P, dimension):
        """ """
        return P / dimension

    def get_moment(self, q_u, req_width, width, wall_type):
        """ """
        l = self.critical_length(req_width, width, wall_type)  # ft
        return q_u * l ** 2 / 2

    def critical_length(self, ftng_width, width, wall_type=None):
        """ """
        if wall_type == "masonry":
            return (ftng_width - (width / 12)) / 2 + (0.25 * width / 12)
        elif wall_type == "concrete":
            return (ftng_width - (width / 12)) / 2

    def get_k_bar(self, m_u, phi, b, d):
        """ """
        return m_u * 12 / (phi * b * (d ** 2))

    def get_rho(self, k_bar):
        """ """
        a = (-0.59 * (self.f_y ** 2)) / self.f_c
        b = self.f_y
        c = -k_bar * 1000
        rho = (-b + math.sqrt((b ** 2) - (4 * a * c))) / (2 * a)

        epsilon_t = self.get_epsilon_t(rho)
        phi = self.get_phi(epsilon_t)

        if phi < 0.9:
            k_bar = self.get_k_bar(m_u, phi, b, d)
            c = -k_bar * 1000
            rho = (-b + math.sqrt((b ** 2) - (4 * a * c))) / (2 * a)

        return self.round(rho, 4)

    def get_epsilon_t(self, rho):
        """ """
        return (0.002555 * self.f_c * self.beta_1 / (rho * self.f_y)) - 0.003

    def get_phi(self, epsilon_t):
        """ """
        if epsilon_t < self.epsilon_y:
            return 0.65
        elif epsilon_t > 0.005:
            return 0.9
        else:
            return 0.65 + (
                (0.25 / (0.005 - self.epsilon_y)) * (epsilon_t - self.epsilon_y)
            )

    def get_reqd_area(self, rho, b, d):
        """Calculates the minimum flexural reinforcement required by analysis (ACI Section 9.6.1.1)

        rho = ratio of tension steel area to effective concrete area
        b = section width
        d = effective depth of steel
        """

        return rho * b * d

    def get_min_beam(self, b, d):
        """Calculates the minimum flexural reinforcement for nonprestressed beams
        as required by ACI Section 9.6.1.2
        """
        a = (3 * math.sqrt(self.f_c) / self.f_y) * b * d
        b = (200 / self.f_y) * b * d
        min_area_beam = max(a, b)

        return min_area_beam

    def get_min_slab(self, b, h):
        """ """
        if self.f_y < 60000:
            return 0.0020 * b * h * 12
        else:
            a = ((0.0018 * 60000) / self.f_y) * b * h * 12
            b = 0.0014 * b * h
            min_area_slab = max(a, b)
            return min_area_slab

    def aci_sec9_6_1_3(self, reqd_area):
        """ """
        return (4 / 3) * reqd_area

    def get_min_area(self, b, d, h, reqd_area):
        """ """
        min_area_beam = self.get_min_beam(b, d)
        min_area_slab = self.get_min_slab(b, h)
        sec_9_6_1_3 = self.aci_sec9_6_1_3(reqd_area)

        return max(min(min_area_beam, sec_9_6_1_3), min_area_slab)


class WallFooting(Footing):
    def __init__(
        self,
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
    ):
        super().__init__(f_c, w_c, conc_type, grade)
        self.h = 1.5  # ft
        self.d = self.get_d(self.h, "wall")  # in

        self.design_wall_footing(
            precision,
            wall_width,
            wall_type,
            d_l,
            l_l,
            a_s_p,
            bottom,
            bar_coat,
            w_e,
        )

    def design_wall_footing(
        self,
        precision,
        wall_width,
        wall_type,
        d_l,
        l_l,
        a_s_p,
        bottom,
        bar_coat,
        w_e,
    ):
        load = d_l + l_l  # k/ft
        factored_load = self.factor_loads(d_l, l_l)  # k/ft
        net_asp = self.net_asp(a_s_p, w_e, self.h, bottom)  # ksf
        req_width = self.find_req_width(load, net_asp, precision)  # ft
        q_u = self.factored_soil_pressure(factored_load, req_width)  # ksf
        phi_vn = self.check_one_way_shear(q_u, req_width, wall_width)
        m_u = self.get_moment(q_u, req_width, wall_width, wall_type)
        k_bar = self.get_k_bar(m_u, 0.9, 12, self.d)
        rho = self.get_rho(k_bar)
        reqd_area = self.get_reqd_area(rho, 12, self.d)
        min_area = self.get_min_area(12, self.d, self.h, reqd_area)

        print(net_asp, req_width, q_u, phi_vn, m_u, k_bar, rho, reqd_area, min_area)

    def find_req_width(self, load, net_asp, precision):
        """returns required width for wall footing, rounded up to the nearest inch."""
        return self.round_to_upper((load / net_asp), precision)

    def check_one_way_shear(self, q_u, req_width, wall_width):
        """ """
        v_u = q_u * 1 * (((req_width - (wall_width / 12)) / 2) - (self.d / 12))  # kip
        v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * self.d) / 1000  # kip
        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.get_d(self.h, "wall")
            v_u = q_u * 1 * (((req_width - (wall_width) / 12) / 2) - (new_d / 12))
            v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c
            self.d = new_d

        if phi_vn < v_u:
            self.d = self.round_to_upper(
                (v_u * 1000 / (2 * self.lam * 0.75 * math.sqrt(self.f_c) * 12))
            )  # in.
            self.h = self.d + 3 + ((8 / 8) / 2)
            v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * new_d) / 1000  # kip
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
        grade,
        a_s_p,
        bottom,
        width_restriction,
        bar_coat,
        col_loc,
        conc_type,
        w_c,
        w_e,
    ):
        super().__init__(f_c, w_c, conc_type, grade)
        self.h = 2  # ft.
        self.d = self.get_d(self.h, "column")  # in

        self.design_column_footing(
            precision,
            width,
            d_l,
            l_l,
            a_s_p,
            bottom,
            width_restriction,
            bar_coat,
            col_loc,
            w_e,
        )

    def design_column_footing(
        self,
        precision,
        width,
        d_l,
        l_l,
        a_s_p,
        bottom,
        width_restriction,
        bar_coat,
        col_loc,
        w_e,
    ):
        load = d_l + l_l  # kip
        factored_load = self.factor_loads(d_l, l_l)  # kip
        net_asp = self.net_asp(a_s_p, w_e, self.h, bottom)  # ksf
        req_area = self.find_req_area(load, net_asp)  # sqft
        req_dims = self.find_req_dims(req_area, width_restriction, precision)  # ft
        actual_area = req_dims[0] * req_dims[1]  # sqft
        q_u = self.factored_soil_pressure(factored_load, actual_area)  # ksf
        two_way_shear = self.check_two_way_shear(
            q_u, actual_area, width, self.d, col_loc
        )
        one_way_shear = self.check_one_way_shear(q_u, req_dims, width, self.d)
        print(
            net_asp, req_area, req_dims, actual_area, q_u, two_way_shear, one_way_shear
        )

    def find_req_area(self, load, net_asp):
        """returns required area for column footing rounded up to the nearest inch"""
        return load / net_asp

    def find_req_dims(self, area, max_width, precision):
        """returns footing dimensions"""

        if max_width:
            long_side = self.round_to_upper((area / max_width), precision)
            return (max_width, long_side)
        else:
            side = self.round_to_upper(math.sqrt(area), precision)
            return (side, side)

    def check_two_way_shear(self, q_u, area, width, d, col_loc):
        """ """
        a = width + d  # in.
        b_0 = 4 * a  # in.
        v_u = q_u * (area - ((a / 12) ** 2))  # kip
        v_c = self.aci_sec22_6_5_2(d, b_0, col_loc)  # kip
        phi_vn = 0.75 * v_c  # kip

        while phi_vn < v_u:
            self.h += 1 / 12
            new_d = self.get_d(self.h, "colmumn")
            new_a = width + new_d
            new_b_0 = 4 * a
            v_u = q_u * (area - ((new_a / 12) ** 2))
            v_c = self.aci_sec22_6_5_2(new_d, new_b_0, col_loc) / 1000
            phi_vn = 0.75 * v_c
            self.d = new_d

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.get_d(self.h, "colmumn")
            new_a = width + new_d
            new_b_0 = 4 * a
            v_u = q_u * (area - ((new_a / 12) ** 2))
            v_c = self.aci_sec22_6_5_2(new_d, new_b_0, col_loc) / 1000
            phi_vn = 0.75 * v_c
            self.d = new_d

        return phi_vn

    def aci_sec22_6_5_2(self, d, b_0, col_loc):
        """ """
        alpha_s = self.find_alpha_s(col_loc)

        v_ca = (4 * self.lam * math.sqrt(self.f_c) * b_0 * d) / 1000
        v_cb = (6 * self.lam * math.sqrt(self.f_c) * b_0 * d) / 1000
        v_cc = (
            (((alpha_s * d) / b_0) + 2) * self.lam * math.sqrt(self.f_c) * b_0 * d
        ) / 1000

        return min(v_ca, v_cb, v_cc)

    def find_alpha_s(self, col_loc):
        """ """
        if col_loc == "interior":
            return 40
        elif col_loc == "edge":
            return 30
        elif col_loc == "corner":
            return 20

    def check_one_way_shear(self, q_u, dims, col_size, d):
        """ """
        v_u = q_u * dims[0] * ((dims[1] - (col_size / 12)) / 2 - (d / 12))  # kip
        v_c = (2 * self.lam * math.sqrt(self.f_c) * (dims[0] * 12) * d) / 1000  # kip

        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.get_d(self.h, "column")
            v_u = q_u * dims[0] * ((dims[1] - col_size) / (12 * 2) - (new_d / 12))
            v_c = (
                2 * self.lam * math.sqrt(self.f_c) * (dims[0] * 12) * new_d
            ) / 1000  # kip
            phi_vn = 0.75 * v_c
            self.d = new_d

        if phi_vn < v_u:
            self.d = self.round_to_upper(
                (
                    v_u
                    * 1000
                    / (2 * self.lam * 0.75 * math.sqrt(self.f_c) * dims[0] * 12)
                )
            )  # in.
            self.h = self.d + 3 + (8 / 8)
            v_c = (
                2 * self.lam * math.sqrt(self.f_c) * (dims[0] * 12) * self.d
            ) / 1000  # kip
            phi_vn = 0.75 * v_c

        return phi_vn
