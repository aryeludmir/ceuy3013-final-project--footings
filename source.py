import math


class Footing:
    def __init__(self, f_c, w_c, conc_type, grade, ftng_type):
        self.f_c = f_c
        self.w_c = w_c
        self.lam = self.get_lam(conc_type)
        self.beta_1 = self.get_beta_1(f_c)
        self.f_y, self.epsilon_y = self.get_steel_props(grade)

        if ftng_type == "wall":
            self.h = 1.5  # ft
            self.d = self.get_d("wall")  # in
        elif ftng_type == "column":
            self.h = 2  # ft
            self.d = self.get_d("column")  # in

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

    def get_d(self, ftng_type, bar_size=8):
        """ """
        if ftng_type == "wall":
            return (self.h * 12) - 3 - ((bar_size / 8) / 2)
        else:
            return (self.h * 12) - 3 - (bar_size / 8)

    def factor_loads(self, d_l, l_l):
        """Calculates the minimum design load by multiplying service loads by given factors (ACI Section 5.3.1).
        For columns the result is in kips, and for walls the result is in kip/ft.
        NOTE: This ACI section is slightly modified for our purpose. See ACI Code, Section 5.3 for more details.
        """
        return (1.2 * d_l) + (1.6 * l_l)

    def net_asp(self, asp, w_e, bottom):
        """Returns the net allowable soil pressure in ksf"""
        return (asp - (w_e * (bottom - self.h)) - (self.w_c * self.h)) / 1000

    def round_up_to_precision(self, x, precision=0.5):
        """ """
        ceil = math.ceil(x)
        temp1 = ceil
        temp2 = ceil

        if (temp1 - x) > 0.5:
            temp1 -= 0.5

        while (temp2 - x) > precision:
            temp2 -= precision

        return min(temp1, temp2)

    def round_up(self, x, n):
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

    def get_k_bar(self, m_u, phi, b):
        """ """
        return m_u * 12 / (phi * b * (self.d ** 2))

    def get_rho(self, k_bar):
        """ """
        a = (-0.59 * (self.f_y ** 2)) / self.f_c
        b = self.f_y
        c = -k_bar * 1000
        rho = (-b + math.sqrt((b ** 2) - (4 * a * c))) / (2 * a)

        epsilon_t = self.get_epsilon_t(rho)
        phi = self.get_phi(epsilon_t)

        if phi < 0.9:
            k_bar = self.get_k_bar(m_u, phi, b)
            c = -k_bar * 1000
            rho = (-b + math.sqrt((b ** 2) - (4 * a * c))) / (2 * a)

        return self.round_up(rho, 4)

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

    def get_reqd_area(self, rho, b):
        """Calculates the minimum flexural reinforcement required by analysis (ACI Section 9.6.1.1)

        rho = ratio of tension steel area to effective concrete area
        b = section width
        d = effective depth of steel
        """

        return rho * b * self.d

    def get_min_beam(self, b):
        """Calculates the minimum flexural reinforcement for nonprestressed beams
        as required by ACI Section 9.6.1.2
        """
        a = (3 * math.sqrt(self.f_c) / self.f_y) * b * self.d
        b = (200 / self.f_y) * b * self.d
        min_area_beam = max(a, b)

        return min_area_beam

    def get_min_slab(self, b):
        """ """
        if self.f_y < 60000:
            return 0.0020 * b * self.h * 12
        else:
            a = ((0.0018 * 60000) / self.f_y) * b * self.h * 12
            b = 0.0014 * b * self.h
            min_area_slab = max(a, b)
            return min_area_slab

    def aci_sec9_6_1_3(self, reqd_area):
        """ """
        return (4 / 3) * reqd_area

    def get_min_area(self, b, reqd_area):
        """ """
        min_area_beam = self.get_min_beam(b)
        min_area_slab = self.get_min_slab(b)
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
        super().__init__(f_c, w_c, conc_type, grade, "wall")
        self.width = 0
        self.min_steel_area = 0

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
        net_asp = self.net_asp(a_s_p, w_e, bottom)  # ksf
        self.width = self.find_req_width(load, net_asp, precision)  # ft
        q_u = self.factored_soil_pressure(factored_load, self.width)  # ksf
        phi_vn = self.check_one_way_shear(q_u, self.width, wall_width)
        m_u = self.get_moment(q_u, self.width, wall_width, wall_type)
        k_bar = self.get_k_bar(m_u, 0.9, 12)
        rho = self.get_rho(k_bar)
        reqd_area = self.get_reqd_area(rho, 12)
        self.min_steel_area = self.get_min_area(12, reqd_area)

        print(
            net_asp,
            self.width,
            q_u,
            phi_vn,
            m_u,
            k_bar,
            rho,
            reqd_area,
            self.min_steel_area,
        )

    def find_req_width(self, load, net_asp, precision):
        """returns required width for wall footing, rounded up to the nearest inch."""
        return self.round_up_to_precision((load / net_asp), precision)

    def check_one_way_shear(self, q_u, req_width, wall_width):
        """ """
        v_u = q_u * 1 * (((req_width - (wall_width / 12)) / 2) - (self.d / 12))  # kip
        v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * self.d) / 1000  # kip
        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            new_d = self.get_d("wall")
            v_u = q_u * 1 * (((req_width - (wall_width) / 12) / 2) - (new_d / 12))
            v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c
            self.d = new_d

        if phi_vn < v_u:
            self.d = self.round_up_to_precision(
                (v_u * 1000 / (2 * self.lam * 0.75 * math.sqrt(self.f_c) * 12))
            )  # in.
            self.h = self.d + 3 + ((8 / 8) / 2)
            v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c

        return phi_vn

    def __str__(self):
        """ """
        return f"Footing width: {self.width} ft, Depth: {round(self.h, 2)} ft, Minimum Required Steel: {round(self.min_steel_area, 2)} sqin/ft"


class ColumnFooting(Footing):
    def __init__(
        self,
        precision,
        width,
        length,
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
        super().__init__(f_c, w_c, conc_type, grade, "column")
        self.dimensions = 0
        self.length_reqd_area = 0
        self.width_reqd_area = 0
        self.bearing_strength = 0

        self.design_column_footing(
            precision,
            width,
            length,
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
        length,
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
        net_asp = self.net_asp(a_s_p, w_e, bottom)  # ksf
        req_area = self.find_req_area(load, net_asp)  # sqft
        self.dims = self.find_req_dims(req_area, width_restriction, precision)  # ft
        actual_area = self.dims[0] * self.dims[1]  # sqft
        q_u = self.factored_soil_pressure(factored_load, actual_area)  # ksf
        two_way_shear = self.check_two_way_shear(q_u, actual_area, width, col_loc)
        one_way_shear = self.check_one_way_shear(q_u, self.dims, width)
        print(
            net_asp, req_area, self.dims, actual_area, q_u, two_way_shear, one_way_shear
        )

    def find_req_area(self, load, net_asp):
        """returns required area for column footing rounded up to the nearest inch"""
        return load / net_asp

    def find_req_dims(self, area, max_width, precision):
        """returns footing dimensions"""

        if max_width:
            long_side = self.round_up_to_precision((area / max_width), precision)
            return (max_width, long_side)
        else:
            side = self.round_up_to_precision(math.sqrt(area), precision)
            return (side, side)

    def check_two_way_shear(self, q_u, area, width, col_loc):
        """ """

        def v_u(self, width, q_u, area):
            a = width + self.d  # in.
            v_u = q_u * (area - ((a / 12) ** 2))  # kip
            return v_u

        def phi_vn(self, width, col_loc):
            a = width + self.d
            b_0 = 4 * a  # in.
            v_c = self.aci_sec22_6_5_2(b_0, col_loc)  # kip
            phi_vn = 0.75 * v_c  # kip
            return phi_vn

        v_u = v_u(self, width, q_u, area)  # kip
        phi_vn = phi_vn(self, width, col_loc)  # kip

        while phi_vn < v_u:
            self.h += 1 / 12
            self.d = self.get_d(self.h, "colmumn")
            v_u = v_u(self, width, q_u, area)  # kip
            phi_vn = phi_vn(self, width, col_loc)  # kip

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            self.d = self.get_d(self.h, "colmumn")
            v_u = v_u(self, width, q_u, area)  # kip
            phi_vn = phi_vn(self, width, col_loc)  # kip

        return phi_vn

    def aci_sec22_6_5_2(self, b_0, col_loc):
        """ """
        alpha_s = self.find_alpha_s(col_loc)

        v_ca = (4 * self.lam * math.sqrt(self.f_c) * b_0 * self.d) / 1000
        v_cb = (6 * self.lam * math.sqrt(self.f_c) * b_0 * self.d) / 1000
        v_cc = (
            (((alpha_s * self.d) / b_0) + 2)
            * self.lam
            * math.sqrt(self.f_c)
            * b_0
            * self.d
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

    def check_one_way_shear(self, q_u, dims, col_size):
        """ """
        v_u = q_u * dims[0] * ((dims[1] - (col_size / 12)) / 2 - (self.d / 12))  # kip
        v_c = (
            2 * self.lam * math.sqrt(self.f_c) * (dims[0] * 12) * self.d
        ) / 1000  # kip

        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            self.d = self.get_d(self.h, "column")
            v_u = q_u * dims[0] * ((dims[1] - col_size) / (12 * 2) - (self.d / 12))
            v_c = (
                2 * self.lam * math.sqrt(self.f_c) * (dims[0] * 12) * self.d
            ) / 1000  # kip
            phi_vn = 0.75 * v_c

        if phi_vn < v_u:
            self.d = self.round_up_to_precision(
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
