import math


class Footing:
    """
    A class used to represent a reinforced concrete footings.
    This is the base (or parent) class for WallFooting and
    ColumnFooting classes.

    Attributes
    ----------
    name : str
        footing ID
    f_c : int
        concrete compression strength (f-prime-c) in psi
    w_c : int
        density of concrete in pcf
    lam : float
        lambda - a modification factor reflecting lower tensile strengths of
        lightweight concrete relative to normal-weight conrete
    beta_1 : float
        a factor that is a function of the strength of the concrete
    f_y : int
        reinforcing steel yield strength in psi
    epsilon_y : float
        reinforcing steel yield strain

    Methods
    ------

    """

    def __init__(self, name, log, f_c, w_c, conc_type, grade, ftng_type):
        """ """

        self.name = name
        self.log = log
        self.f_c = f_c
        self.w_c = w_c
        self.lam = self.set_lam(conc_type)
        self.beta_1 = self.set_beta_1()
        self.f_y, self.epsilon_y = self.get_steel_props(grade)

        if ftng_type == "wall":
            self.h = 1.5  # ft
            self.set_d("wall")  # in
        elif ftng_type == "column":
            self.h = 2  # ft
            self.set_d("column")  # in

    def set_lam(self, conc_type):
        """This method returns "lambda". To account for properties of
        lightweight concrete, a modification factor "lambda" is used as
        a multiplier for sqrt(f_c). See ACI 318-14 Sec 19.2.4.1 and 19.2.4.2.

        Parameters
        ----------
        conc_type : str
            Type of concrete - Normal weight ("nw"), Lightweight ("lw")
            or sand-lightweight ("s_lw")

        """
        self.log.write("Calulating lambda in acordance with ACI 318-14 Sec 19.2.4.2:\n")

        if conc_type == "nw":
            self.log.write("\tConcrete is normal-weight. Lambda = 1.0\n")
            return 1.0
        elif conc_type == "lw":
            self.log.write("\tConcrete is lightweight. Lambda = 0.75\n")
            return 0.75
        elif conc_type == "s_lw":
            self.log.write("\tConcrete is sand-lightweight. Lambda = 0.85\n")
            return 0.85

    def set_beta_1(self):
        """Returns beta_1. A factor that is a function of the strength of
        the concrete. See ACI 318-14 Sec 22.2.2.4.3
        """
        self.log.write(
            "Calulating beta_1 in acordance with ACI 318-14 Sec 22.2.2.4.3:\n"
        )

        if self.f_c > 4000:
            eq = 0.85 - (0.05 * (self.f_c - 4000) / 1000)
            beta_1 = max(eq, 0.65)
            self.log.write(f"\tf-prime-c is {self.f_c}. beta_1 = {beta_1}\n")
            return beta_1
        else:
            self.log.write(f"\tf-prime-c is {self.f_c}. beta_1 = 0.85\n")
            return 0.85

    def get_steel_props(self, grade):
        """Returns two reinforcing steel properties:
            f_y : yield strength in psi
            epsilon_y : yield strain

        Parameters
        ----------
        grade : int
            reinforcinfg steel grade designation

        """

        if grade == 40:
            self.log.write(
                "Reinforcing steel Grade 40:\n\tf_y = 40000 psi, epsilon_y = 0.00138\n"
            )
            return (40000, 0.00138)
        elif grade == 60:
            self.log.write(
                "Reinforcing steel Grade 60:\n\tf_y = 60000 psi, epsilon_y = 0.00207\n"
            )
            return (60000, 0.00207)
        elif grade == 75:
            self.log.write(
                "Reinforcing steel Grade 75:\n\tf_y = 75000 psi, epsilon_y = 0.00259\n"
            )
            return (75000, 0.00259)

    def set_d(self, ftng_type, bar_size=8):
        """Returns the footing's effective depth "d" in inches. "d" is
        the centroid of the reinforcing steel bars. For a good approximation,
        a bar size diameter of 8 inches is assumed for a defualt value.

        Parameters
        ----------
        ftng_type : str
            describes footing type - wall or column
        bar_size : int
            number of bar (default is #8)
        """

        self.log.write(
            f"Caluclating d with a footing thickness of {round(self.h, 3)} ft:\n"
        )

        if ftng_type == "wall":
            self.d = (self.h * 12) - 3 - ((bar_size / 8) / 2)
            self.log.write(f"\td = {round(self.d, 2)}\n")
            pass
        else:
            self.d = (self.h * 12) - 3 - (bar_size / 8)
            self.log.write(f"\td = {round(self.d, 2)}\n")
            pass

    # def factor_loads(self, d_l, l_l):
    #     """Calculates the minimum design load by multiplying service loads by given factors (ACI Section 5.3.1).
    #     For columns the result is in kips, and for walls the result is in kip/ft.
    #     NOTE: This ACI section is slightly modified for our purpose. See ACI Code, Section 5.3 for more details.
    #     """
    #     return (1.2 * d_l) + (1.6 * l_l)

    def net_asp(self, asp, w_e, bottom):
        """Returns the net allowable soil pressure in ksf. The net allowable soil pressure
        is calculated using factored loads as put forth in ACI 318-14 Sec 5.3.1 equation b.

        Paramaters
        ----------
        asp : int
            the total allowable soil pressure in psf
        w_e : int
            the density of the earth in pcf
        bottom : float
            bottom of footing relative to earth surface in feet

        """

        self.log.write(
            f"Calculating net allowable soil pressure: \n\tASP = {asp} psf, w_e = {w_e} pcf, bottom of footing {bottom} ft below eartth surface.\n"
        )

        net_asp = (asp - (w_e * (bottom - self.h)) - (self.w_c * self.h)) / 1000

        self.log.write(f"\tNet allowable soil pressure = {net_asp} ksf.\n")

        return net_asp

    def factored_soil_pressure(self, d_l, l_l, dimension):
        """Returns factored soil pressure from superimposed loads
        tp be used for footing design.

        Parameters
        ----------
        d_l : float
            service dead load to be supported
        l_l : float
            service live load to be supported
        dimesion : float
            dimension of footing (width for wall, area for column)
        """

        self.log.write("Calculating factored soil pressure: \n")
        factored_asp = ((1.2 * d_l) + (1.6 * l_l)) / dimension
        self.log.write(f"\tFactored soil pressure = {round(factored_asp, 2)} ksf.\n")

        return factored_asp

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

    def round_up_to_precision(self, x, precision):
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


class WallFooting(Footing):
    def __init__(
        self,
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
    ):
        super().__init__(name, log, f_c, w_c, conc_type, grade, "wall")
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
        # load = d_l + l_l  # k/ft
        # factored_load = self.factor_loads(d_l, l_l)  # k/ft
        net_asp = self.net_asp(a_s_p, w_e, bottom)  # ksf
        self.width = self.get_req_width(d_l, l_l, net_asp, precision)  # ft
        q_u = self.factored_soil_pressure(d_l, l_l, self.width)  # ksf
        phi_vn = self.check_one_way_shear(q_u, self.width, wall_width)
        m_u = self.get_moment(q_u, wall_width, wall_type)
        k_bar = self.get_k_bar(m_u, 0.9, 12)
        rho = self.get_rho(k_bar)
        reqd_area = self.get_reqd_area(rho, 12)
        self.min_steel_area = self.get_min_area(12, reqd_area)

    def get_req_width(self, d_l, l_l, net_asp, precision):
        """Returns required width for wall footing, rounded up to desired precision.

        Parameters
        ----------
        d_l : float
            service dead load to be supported in kip/ft
        l_l : float
            service live load to be supported in kip/ft
        net_asp : float
            net allowable soil pressure below footing in psf
        precision : float
            desired accuracy of footing dimensions

        """

        self.log.write("Calculating required footing width:\n")

        reqd_width = (d_l + l_l) / net_asp
        used_width = self.round_up_to_precision(reqd_width, precision)

        self.log.write(
            f"\tRequired footing width: {round(reqd_width, 2)} ft.\n\tUse {round(used_width, 3)} ft \n"
        )

        return used_width

    def check_one_way_shear(self, q_u, req_width, wall_width):
        """ """
        v_u = q_u * 1 * (((req_width - (wall_width / 12)) / 2) - (self.d / 12))  # kip
        v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * self.d) / 1000  # kip
        phi_vn = 0.75 * v_c  # kip

        while phi_vn > (1.5 * v_u):
            self.h -= 1 / 12
            self.set_d("wall")
            v_u = q_u * 1 * (((req_width - (wall_width) / 12) / 2) - (self.d / 12))
            v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * self.d) / 1000  # kip
            phi_vn = 0.75 * v_c

        if phi_vn < v_u:
            self.d = self.round_up_to_precision(
                (v_u * 1000 / (2 * self.lam * 0.75 * math.sqrt(self.f_c) * 12))
            )  # in.
            self.h = (self.d + 3 + ((8 / 8) / 2)) / 12
            v_c = (2 * self.lam * math.sqrt(self.f_c) * 12 * new_d) / 1000  # kip
            phi_vn = 0.75 * v_c

        return phi_vn

    def get_moment(self, q_u, wall_width, wall_type):
        """ """

        def critical_length(self, wall_width, wall_type):
            """ """
            if wall_type == "masonry":
                return (self.width - (wall_width / 12)) / 2 + (0.25 * wall_width / 12)
            elif wall_type == "concrete":
                return (self.width - (wall_width / 12)) / 2

        l = critical_length(self, wall_width, wall_type)  # ft

        return q_u * l ** 2 / 2

    def get_ftng_dict(self):
        """ """
        d = {
            "id": self.name,
            "ftng_width_ft": round(self.width, 3),
            "ftng_depth_ft": round(self.h, 3),
            "min_steel_sqin/ft": round(self.min_steel_area, 2),
        }

        return d

    def __str__(self):
        """ """
        return f"Footing width: {self.width} ft\nDepth: {round(self.h, 2)} ft\nMinimum Required Steel: {round(self.min_steel_area, 2)} sqin/ft"


class ColumnFooting(Footing):
    def __init__(
        self,
        name,
        log,
        precision,
        col_width,
        col_length,  # this is a feature to be added
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
        super().__init__(name, log, f_c, w_c, conc_type, grade, "column")
        self.dims = 0
        self.length_reqd_area = 0
        self.width_reqd_area = 0
        self.bearing_strength = 0
        self.min_steel_area_short = 0
        self.min_steel_area = 0

        self.design_column_footing(
            precision,
            col_width,
            col_length,
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
        col_width,
        col_length,
        d_l,
        l_l,
        a_s_p,
        bottom,
        width_restriction,
        bar_coat,
        col_loc,
        w_e,
    ):
        # load = d_l + l_l  # kip
        # factored_load = self.factor_loads(d_l, l_l)  # kip
        net_asp = self.net_asp(a_s_p, w_e, bottom)  # ksf
        self.dims, area = self.get_dimensions(
            d_l, l_l, net_asp, width_restriction, precision
        )  # sqft
        # self.dims = self.find_req_dims(req_area, width_restriction, precision)  # ft
        # actual_area = self.dims[0] * self.dims[1]  # sqft
        q_u = self.factored_soil_pressure(d_l, l_l, area)  # ksf
        two_way_shear = self.check_two_way_shear(q_u, area, col_width, col_loc)
        one_way_shear = self.check_one_way_shear(q_u, self.dims, col_width)
        m_u = self.get_m_u(q_u, self.dims, col_width)
        k_bar = self.get_k_bar(m_u, 0.9, min(self.dims) * 12)
        rho = self.get_rho(k_bar)
        reqd_area = self.get_reqd_area(rho, min(self.dims) * 12)
        self.min_steel_area = self.get_min_area(min(self.dims) * 12, reqd_area)
        self.min_steel_area_short = self.min_steel_area

        if self.dims[0] != self.dims[1]:
            short_mu = self.get_short_mu(q_u, self.dims, col_width)
            short_k_bar = self.get_k_bar(short_mu, 0.9, max(self.dims) * 12)
            short_rho = self.get_rho(short_k_bar)
            short_reqd_area = self.get_reqd_area(short_rho, max(self.dims) * 12)
            self.min_steel_area_short = self.get_min_area(
                max(self.dims) * 12, short_reqd_area
            )

    def get_dimensions(self, d_l, l_l, net_asp, max_width, precision):
        """Returns required footing dimensions and area, rounded up to desired precision.

        Parameters
        ----------
        d_l : float
            service dead load to be supported in kips
        l_l : float
            service live load to be supported in kips
        net_asp : float
            net allowable soil pressure below footing in psf
        max_width : float
            footing width restriction in ft
        precision : float
            desired accuracy of footing dimensions

        """
        self.log.write("Calculating required footing area:\n")

        reqd_area = (d_l + l_l) / net_asp
        self.log.write(f"\tRequired footing area: {round(reqd_area, 2)} square ft\n")

        if max_width:
            long_side = self.round_up_to_precision((reqd_area / max_width), precision)
            dims = (max_width, long_side)
        else:
            side = self.round_up_to_precision(math.sqrt(reqd_area), precision)
            dims = (side, side)

        actual_area = dims[0] * dims[1]
        self.log.write(
            f"\tUse (in ft): {dims}\n\tActual area provided: {actual_area} sq ft\n"
        )

        return dims, actual_area

    # def find_req_dims(self, area, max_width, precision):
    #     """returns footing dimensions"""

    #     if max_width:
    #         long_side = self.round_up_to_precision((area / max_width), precision)
    #         return (max_width, long_side)
    #     else:
    #         side = self.round_up_to_precision(math.sqrt(area), precision)
    #         return (side, side)

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
            self.set_d("colmumn")
            v_u = v_u(self, width, q_u, area)  # kip
            phi_vn = phi_vn(self, width, col_loc)  # kip

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            self.set_d("colmumn")
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
            self.set_d(self.h, "column")
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
                ),
                0.5,
            )  # in.
            self.h = (self.d + 3 + (8 / 8)) / 12
            v_c = (
                2 * self.lam * math.sqrt(self.f_c) * (dims[0] * 12) * self.d
            ) / 1000  # kip
            phi_vn = 0.75 * v_c

        return phi_vn

    def get_m_u(self, q_u, dims, col_width):
        """ """
        l = (max(dims) - (col_width / 12)) / 2
        mu = (q_u * min(dims) * l ** 2) / 2

        return mu

    def get_short_mu(self, q_u, dims, col_width):
        """ """
        l = (min(dims) - (col_width / 12)) / 2
        mu = (q_u * max(dims) * l ** 2) / 2

        return mu

    def get_ftng_dict(self):
        """ """
        d = {
            "id": self.name,
            "ftng_dimensions_ft": self.dims,
            "ftng_depth_ft": round(self.h, 3),
            "min_steel_in_long_dim_sqin": round(self.min_steel_area, 3),
            "min_steel_in_short_dim_sqin": round(self.min_steel_area_short, 3),
        }

        return d

    def __str__(self):
        """ """
        return f"Footing dimensions: {self.dims} ft\nDepth: {round(self.h, 2)} ft\nMinimum Required Steel Along {max(self.dims)} ft Direction: {round(self.min_steel_area, 2)} sqin\nMinimum Required Steel Along {min(self.dims)} ft Direction: {round(self.min_steel_area_short, 2)} sqin"
