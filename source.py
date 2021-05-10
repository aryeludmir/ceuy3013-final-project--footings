import math


class Footing:
    """
    A class used to represent a reinforced concrete footing.
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
        """Returns the modification factor "lambda".

        To account for properties of lightweight concrete, a modification factor
        "lambda" is used as a multiplier for sqrt(f_c).
        See ACI 318-14 Sec 19.2.4.1 and 19.2.4.2.

        Parameters
        ----------
        conc_type : str
            Type of concrete - Normal weight ("nw"), Lightweight ("lw")
            or sand-lightweight ("s_lw")

        """
        self.log.write("Get lambda (ACI 318-14 Sec 19.2.4.2)...\n")

        if conc_type == "nw":
            self.log.write("-> Concrete is normal-weight. Lambda = 1.0\n")
            return 1.0
        elif conc_type == "lw":
            self.log.write("-> Concrete is lightweight. Lambda = 0.75\n")
            return 0.75
        elif conc_type == "s_lw":
            self.log.write("-> Concrete is sand-lightweight. Lambda = 0.85\n")
            return 0.85

    def set_beta_1(self):
        """Returns the facror beta_1.

        beta_1 is a  factor that is a function of the strength of the concrete.
        See ACI 318-14 Sec 22.2.2.4.3
        """
        self.log.write("Calulate beta_1 (ACI 318-14 Sec 22.2.2.4.3)...\n")

        if self.f_c > 4000:
            eq = 0.85 - (0.05 * (self.f_c - 4000) / 1000)
            beta_1 = max(eq, 0.65)
            self.log.write(
                f"-> f-prime-c is {self.f_c} -----> beta_1 = {beta_1}\n")
            return beta_1
        else:
            self.log.write(
                f"-> f-prime-c is {self.f_c} -----> beta_1 = 0.85\n")
            return 0.85

    def get_steel_props(self, grade):
        """Returns two reinforcing steel properties.

        The properties are f_y : yield strength in psi; epsilon_y : yield strain

        Parameters
        ----------
        grade : int
            reinforcinfg steel grade designation

        """

        self.log.write(
            f"Get properties for Grade {grade} reinforcing steel...\n")

        if grade == 40:
            self.log.write("-> f_y = 40000 psi, epsilon_y = 0.00138\n")
            return (40000, 0.00138)
        elif grade == 60:
            self.log.write("-> f_y = 60000 psi, epsilon_y = 0.00207\n")
            return (60000, 0.00207)
        elif grade == 75:
            self.log.write("-> f_y = 75000 psi, epsilon_y = 0.00259\n")
            return (75000, 0.00259)

    def set_d(self, ftng_type, bar_size=8):
        """Returns the footing's effective depth "d" in inches.

        "d" is the centroid of the reinforcing steel bars. For a good approximation,
        a bar size diameter of 8 inches is assumed for a defualt value.

        Parameters
        ----------
        ftng_type : str
            describes footing type - wall or column
        bar_size : int
            number of bar (default is #8)
        """

        self.log.write(
            f"Caluclate d for footing thickness h = {round(self.h, 3)} ft...\n"
        )

        if ftng_type == "wall":
            self.d = (self.h * 12) - 3 - ((bar_size / 8) / 2)
            self.log.write(f"-> d = {round(self.d, 2)} in.\n")
            pass
        else:
            self.d = (self.h * 12) - 3 - (bar_size / 8)
            self.log.write(f"-> d = {round(self.d, 2)} in.\n")
            pass

    def net_asp(self, asp, w_e, bottom):
        """Returns the net allowable soil pressure (ASP) in ksf.

        The net ASP is calculated using factored loads as put forth in
        ACI 318-14 Sec 5.3.1 equation b.

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
            f"Calculate net allowable soil pressure...\n-> ASP = {asp} psf, w_e = {w_e} pcf, w_c = {self.w_c} pcf, bottom of footing {bottom} ft below eartth surface.\n"
        )

        net_asp = (asp - (w_e * (bottom - self.h)) -
                   (self.w_c * self.h)) / 1000

        self.log.write(f"-> Net allowable soil pressure = {net_asp} ksf.\n")

        return net_asp

    def factored_soil_pressure(self, d_l, l_l, dimension):
        """Returns factored soil pressure to be used for footing design.

        Parameters
        ----------
        d_l : float
            service dead load to be supported
        l_l : float
            service live load to be supported
        dimesion : float
            dimension of footing (width for wall, area for column)
        """

        self.log.write("Calculate factored soil pressure, q_u... \n")
        factored_asp = ((1.2 * d_l) + (1.6 * l_l)) / dimension
        self.log.write(f"-> q_u = {round(factored_asp, 2)} ksf.\n")

        return factored_asp

    def get_k_bar(self, m_u, phi, b):
        """Returns the coefficient of resistance, k-bar

        Parameters
        ----------
        m_u : float
            bending moment
        phi : float
            strength reduction factor (ACI 318-14 Sec 21.2)
        b : float
            element width

        """

        k_bar = m_u * 12 / (phi * b * (self.d**2))
        self.log.write(f"-> k_bar = {round(k_bar, 4)} ksi -----> ")
        return k_bar

    def solve_for_rho(self, k_bar):
        """Returns reinforcement ratio, rho, and corrects
        phi and k_bar if need be.

        Parameters
        ----------
        k_bar : float
            coefficient of resistance
        """
        a = (-0.59 * (self.f_y**2)) / self.f_c
        b = self.f_y
        c = -k_bar * 1000
        rho = (-b + math.sqrt((b**2) - (4 * a * c))) / (2 * a)
        self.log.write(f"rho = {self.round_up(rho, 4)}\n")
        self.log.write(f"Check assumption that phi = 0.9...\n")

        epsilon_t = self.get_epsilon_t(rho)
        phi = self.get_phi(epsilon_t)

        if phi < 0.9:
            self.log.write(f"-> {phi} < 0.9. Recalculate k_bar...\n")
            k_bar = self.get_k_bar(m_u, phi, b)
            c = -k_bar * 1000
            rho = (-b + math.sqrt((b**2) - (4 * a * c))) / (2 * a)
            self.log.write(f"-> rho = {self.round_up(rho, 4)}\n")

        return self.round_up(rho, 4)

    def get_epsilon_t(self, rho):
        """Returns tensile strain, epsilon_t, for given rho

        Parameters
        ----------
        rho : float
            reinforcement ratio
        """

        return (0.002555 * self.f_c * self.beta_1 / (rho * self.f_y)) - 0.003

    def get_phi(self, epsilon_t):
        """Returns strength reduction factor, phi

        Parameters
        ----------
        epsilon_t : float
            tensile strain
        """

        if epsilon_t < self.epsilon_y:
            self.log.write("-> Compression section -----> phi = 0.65\n")
            return 0.65
        elif epsilon_t > 0.005:
            self.log.write("-> Tension section -----> phi = 0.9 (O.K.)\n")
            return 0.9
        else:
            phi = 0.65 + ((0.25 / (0.005 - self.epsilon_y)) *
                          (epsilon_t - self.epsilon_y))
            self.log.write(
                f"-> Transition section -----> phi = {round(phi, 2)}\n")
            return phi

    def calc_reqd_steel(self, rho, b, ftng_type):
        """Calculates the minimum flexural reinforcement required by analysis
        See ACI 318-14 Sec 9.6.1.1

        Parameters
        ----------
        rho : float
            ratio of tension steel area to effective concrete area
        b : float
            section width
        d : float
            effective depth of steel
        ftng_type : str
            footing type (wall or column)
        """
        self.log.write(
            "Calculate required steel area (ACI 318-14 Sec 9.6.1.1)...\n")
        reqd_area = rho * b * self.d

        if ftng_type == "wall":
            self.log.write(
                f"-> A_s required = {round(reqd_area, 3)} sq_in per foot of wall\n"
            )
        else:
            self.log.write(f"-> A_s required = {round(reqd_area, 3)} sq_in\n")

        return reqd_area

    def get_min_beam(self, b):
        """Calculates the minimum flexural reinforcement for nonprestressed beams
        as required by ACI Section 9.6.1.2

        Parameters
        ----------
        b : float
            element width in inches
        """

        self.log.write(
            "Calculate A_s,min for beams (ACI 318-14 Sec 9.6.1.2)...\n")
        a = (3 * math.sqrt(self.f_c) / self.f_y) * b * self.d
        b = (200 / self.f_y) * b * self.d
        min_area_beam = max(a, b)
        self.log.write(
            f"-> A_s,min for beams = {round(min_area_beam,3)} sq in.\n")

        return min_area_beam

    def get_min_slab(self, b):
        """Calculates the minimum flexural reinforcement for slabs
        as required by ACI Section 7.6.1.1

        Parameters
        ----------
        b : float
            element width in inches
        """

        self.log.write(
            "Calculate A_s,min for slabs (ACI 318-14 Sec 7.6.1.1)...\n")
        if self.f_y < 60000:
            min_are_slab = 0.0020 * b * self.h * 12
        else:
            a = ((0.0018 * 60000) / self.f_y) * b * self.h * 12
            b = 0.0014 * b * self.h
            min_area_slab = max(a, b)

        self.log.write(
            f"-> A_s,min for slabs = {round(min_area_slab,3)} sq in.\n")
        return min_area_slab

    def aci_sec9_6_1_3(self, reqd_area):
        """Calculates the minimum flexural reinforcement for beams as required by
        ACI 318-14 Sec 9.6.1.3

        If A_s provided is at least one-third greater than A_s required by Sec 9.6.1.1,
        then 9.6.1.2 need not be satisfied.

        Parameters
        ----------
        reqd_area : float
            area of steel required by analysis (ACI 318-14 Sec 9.6.1.1)
        """

        self.log.write(
            "Calculate 1.33 x A_s required (ACI 318-14 Sec 9.6.1.3)...\n")
        sec_9_6_1_3 = (4 / 3) * reqd_area
        self.log.write(
            f"-> A_s as required by 9.6.1.3 = {round(sec_9_6_1_3, 3)} sq in.\n"
        )

        return sec_9_6_1_3

    def get_min_reinforcing(self, b, reqd_area):
        """Returns the governing minimum required steel for footing

        The minimum steel required is the maximum of A_s,min for beams, A_s,min
        for slabs, and A_s reqd. Unless as provisioned in Sec 9.6.1.3

        Parameters
        ----------
        b : float
            element width
        reqd_area : float
            minimum required steel reinforcement provided by analysis
        """
        min_area_beam = self.get_min_beam(b)
        min_area_slab = self.get_min_slab(b)

        if reqd_area >= min_area_beam:
            governing = max(min_area_beam, min_area_slab, reqd_area)
        else:
            sec_9_6_1_3 = self.aci_sec9_6_1_3(reqd_area)
            governing = max(min(min_area_beam, sec_9_6_1_3), min_area_slab)

        self.log.write(f"-> Use A_s = {round(governing,3)} sq in.\n")

        return governing

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
        x = x * 10**n
        ceil = math.ceil(x)
        return ceil / (10**n)


class WallFooting(Footing):
    def __init__(self, name, log, precision, wall_width, wall_type, d_l, l_l, f_c, grade, a_s_p, bottom, conc_type, w_c, w_e,):
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
            w_e,
        )

    def design_wall_footing(self, precision, wall_width, wall_type, d_l, l_l, a_s_p, bottom, w_e,):
        self.width = self.get_req_width(d_l, l_l,
                                        a_s_p, w_e, bottom, precision)  # ft
        q_u = self.factored_soil_pressure(d_l, l_l, self.width)  # ksf
        self.check_one_way_shear(q_u, self.width, wall_width)
        steel_reqd = self.get_steel_reqd(q_u, wall_width, wall_type)
        self.min_steel_area = self.get_min_reinforcing(12, steel_reqd)

    def get_req_width(self, d_l, l_l, a_s_p, w_e, bottom, precision):
        """Calculates net allowable soil pressure, and returns
        required width of wall footing, rounded up to desired precision.

        Parameters
        ----------
        d_l : float
            service dead load to be supported in kip/ft
        l_l : float
            service live load to be supported in kip/ft
        asp : int
            the total allowable soil pressure in psf
        w_e : int
            the density of the earth in pcf
        bottom : float
            bottom of footing relative to earth surface in feet
        precision : float
            desired accuracy of footing dimensions

        """
        net_asp = self.net_asp(a_s_p, w_e, bottom)

        self.log.write("Calculate required footing width:\n")

        reqd_width = (d_l + l_l) / net_asp
        used_width = self.round_up_to_precision(reqd_width, precision)

        self.log.write(
            f"-> Required footing width: {round(reqd_width, 2)} ft.\n-> Use {round(used_width, 3)} ft \n"
        )

        return used_width

    def check_one_way_shear(self, q_u, req_width, wall_width):
        """Checks one-way (beam) shear for wall footing, and adjusts
        footing thickness as needed.

        Parameters
        ----------
        q_u : float
            the factored soil pressure in ksf
        req_width : float
            the footing width in ft
        wall_width : float
            the wall width in inches

        """

        def get_v_u(self, q_u, req_width, wall_width):
            """Returns the required shear strength (V_u) in kips.

            V_u is taken at the critical section at a distance equal to
            the effective dephth d away from the face of the wall.
            See ACI 318-14 Sec 9.4.3.2
            """

            self.log.write("Calculate V_u for one-way shear...\n")
            v_u = q_u * 1 * (((req_width - (wall_width / 12)) / 2) -
                             (self.d / 12))
            self.log.write(f"-> V_u = {round(v_u, 3)} kips /ft of wall\n")

            return v_u

        def get_phi_vn(self):
            """Returns the factored concrete nominal shear strength (phi_vn)"""

            self.log.write("Calculate phi_V_n for one-way shear...\n")
            phi_vn = 0.75 * (2 * self.lam * math.sqrt(self.f_c) * 12 *
                             self.d) / 1000
            self.log.write(
                f"-> phi_V_n = {round(phi_vn, 3)} kips /ft of wall\n")

            return phi_vn

        self.log.write("Check one-way shear...\n")
        v_u = get_v_u(self, q_u, req_width, wall_width)  # kip
        phi_vn = get_phi_vn(self)  # kip

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            self.log.write(
                f"-> phi_V_n = {round(phi_vn,3)} >> V_u = {round(v_u, 3)} -----> try footing thickness = {round(self.h,3)} ft\n"
            )
            self.set_d("wall")
            v_u = get_v_u(self, q_u, req_width, wall_width)  # kip
            phi_vn = get_phi_vn(self)  # kip

        if phi_vn < v_u:
            self.d = self.round_up_to_precision(
                (v_u * 1000 /
                 (2 * self.lam * 0.75 * math.sqrt(self.f_c) * 12)))  # in.
            self.h = (self.d + 3 + ((8 / 8) / 2)) / 12
            self.log.write(
                f"-> phi_V_n = {round(phi_vn,3)} < V_u = {round(v_u, 3)} -----> try footing thickness = {round(self.h,3)} ft\n"
            )
            phi_vn = get_phi_vn(self)

        self.log.write(
            f"-> phi_V_n = {round(phi_vn,3)} > V_u = {round(v_u, 3)} (O.K.)\n")

    def get_steel_reqd(self, q_u, wall_width, wall_type):
        """Calculates bending moment and reinforcement ratio. Returns required steel area

        Parameters
        ----------
        q_u : float
            the factored soil pressure in ksf
        wall_width : float
            the wall width in inches
        wall_type : str
            wall type (masonry or concrete)

        """

        self.log.write("Calculate M_u...\n")
        if wall_type == "masonry":
            l = (self.width - (wall_width / 12)) / 2 + (0.25 * wall_width / 12)
            self.log.write(
                f"-> {wall_type} wall -----> critical length = {round(l,2)} ft \n"
            )
        elif wall_type == "concrete":
            l = (self.width - (wall_width / 12)) / 2
            self.log.write(
                f"-> {wall_type} wall -----> critical length = {round(l,2)} ft \n"
            )

        m_u = q_u * l**2 / 2
        self.log.write(f"-> M_u = {round(m_u,2)} kip-ft\n")

        k_bar = self.get_k_bar(m_u, 0.9, 12)
        rho = self.solve_for_rho(k_bar)
        reqd_area = self.calc_reqd_steel(rho, 12, "wall")

        return reqd_area

    def get_ftng_dict(self):
        """ """
        d = {
            "id": self.name,
            "ftng_width": f"{round(self.width, 3)} ft",
            "ftng_depth": f"{round(self.h, 3)} ft",
            "min_steel": f"{round(self.min_steel_area, 2)} sq in per ft",
        }

        return d

    def __str__(self):
        """ """
        return f"Footing width: {round(self.width, 2)} ft\nDepth: {round(self.h, 2)} ft\nMinimum Required Steel: {round(self.min_steel_area, 2)} sqin/ft"


class ColumnFooting(Footing):
    def __init__(self, name, log, precision, col_width, d_l, l_l,
                 f_c, grade, a_s_p, bottom, width_restriction, col_loc, conc_type, w_c, w_e):
        super().__init__(name, log, f_c, w_c, conc_type, grade, "column")
        self.length = 0
        self.width = 0
        self.min_steel_area_width = 0
        self.min_steel_area_length = 0

        self.design_column_footing(precision, col_width, d_l, l_l,
                                   a_s_p, bottom, width_restriction, col_loc, w_e)

    def design_column_footing(self, precision, col_width, d_l, l_l, a_s_p,
                              bottom, width_restriction, col_loc, w_e):
        self.length, self.width = self.get_dimensions(
            d_l, l_l, a_s_p, w_e, bottom, width_restriction, precision)  # sqft
        area = self.length * self.width
        q_u = self.factored_soil_pressure(d_l, l_l, area)  # ksf
        self.check_two_way_shear(q_u, area, col_width, col_loc)
        self.check_one_way_shear(q_u, col_width)

        l = (self.length - (col_width / 12)) / 2
        steel_reqd_length = self.get_steel_reqd(q_u, l, self.width)
        self.min_steel_area_length = self.get_min_reinforcing(
            self.width * 12, steel_reqd_length)
        self.min_steel_area_width = self.min_steel_area_length

        if self.width != self.length:
            self.log.write(
                f"The above calculation was for parallel the {self.length} ft side. Now calculate for the {self.width} ft side...\n")
            l = (self.width - (col_width / 12)) / 2
            steel_reqd_width = self.get_steel_reqd(q_u, l, self.length)
            self.min_steel_area_width = self.get_min_reinforcing(
                self.length * 12, steel_reqd_width)
        else:
            self.log.write(
                f"-> Required steel area the same in both directions for square footing.\n")

    def get_dimensions(self, d_l, l_l, a_s_p, w_e, bottom, max_width, precision):
        """Calculates net allowable soil pressure, and returns
        required footing dimensions and area, rounded up to desired precision.

        Parameters
        ----------
        d_l : float
            service dead load to be supported in kips
        l_l : float
            service live load to be supported in kips
        asp : int
            the total allowable soil pressure in psf
        w_e : int
            the density of the earth in pcf
        bottom : float
            bottom of footing relative to earth surface in feet
        max_width : float
            footing width restriction in ft
        precision : float
            desired accuracy of footing dimensions

        """

        net_asp = self.net_asp(a_s_p, w_e, bottom)

        self.log.write("Calculate required footing area...\n")

        reqd_area = (d_l + l_l) / net_asp
        self.log.write(
            f"-> Required footing area: {round(reqd_area, 2)} square ft\n")

        if max_width:
            long_side = self.round_up_to_precision(
                (reqd_area / max_width), precision)
            l, w = (long_side, max_width)
        else:
            side = self.round_up_to_precision(math.sqrt(reqd_area), precision)
            l, w = (side, side)

        actual_area = l * w
        self.log.write(
            f"-> Use: {l} ft x {w} ft\n-> Actual area provided: {actual_area} sq ft\n"
        )

        return (l, w)

    def check_two_way_shear(self, q_u, area, width, col_loc):
        """Checks two way (punching) shear for column footing,
        and adjusts footing depth when required.

        Parameters
        ----------
        q_u : float
            the factored soil pressure in ksf
        area : float
            the footing area in sq ft
        width : float
            the column width in inches
        col_loc : str
            the location of column on footing (interior, edde, or corner)
        """

        def get_v_u(self, width, q_u, area):
            """Returns required shear strength (V_u) in kips.

            V_u is taken at the critical section so that its perimeter
            b_0 does not come closer to the edge of the column than
            one-half the effective depth.
            See ACI 318-14 Sec 22.6.4.1
            """

            self.log.write(
                "Calculate required shear strenght, V_u (ACI 318-14 Sec 22.6.4.1)...\n"
            )
            a = width + self.d  # in.
            v_u = q_u * (area - ((a / 12)**2))  # kip
            self.log.write(f"-> V_u = {round(v_u,3)} kips\n")

            return v_u

        def get_phi_vn(self, width, col_loc):
            """Returns factored concrete shear strength (phi_V_n) in kips

            phi_V_n is taken as 75% of concrete shear strangth, V_c.
            See ACI 318-14 Sec 21.2 and Sec 22.6.5.2

            """

            a = width + self.d
            b_0 = 4 * a  # in.
            v_c = get_v_c(self, b_0, col_loc)  # kip
            phi_vn = 0.75 * v_c  # kip
            self.log.write(
                "Calculate factored concrete shear strength, phi_V_n (ACI 318-14 Sec 21.2)...\n"
            )
            self.log.write(f"-> phi_V_n = {round(phi_vn, 3)} kips\n")

            return phi_vn

        def get_v_c(self, b_0, col_loc):
            """Returns concrete shear strength V_c

            See ACI Sec 22.6.5.2

            Parameters
            ----------
            b_0 : float
                perimeter of critical section taken at a distance d/2 from column edge
            """

            def get_alpha_s(self, col_loc):
                """Returns alpha_s

                See ACI 318-14 Sec 22.6.5.3
                """
                if col_loc == "interior":
                    return 40
                elif col_loc == "edge":
                    return 30
                elif col_loc == "corner":
                    return 20

            self.log.write(
                f"Calcukate V_c for two two-way shear (ACI Sec 22.6.5.2)...\n")

            v_ca = (4 * self.lam * math.sqrt(self.f_c) * b_0 * self.d) / 1000
            self.log.write(f"-> v_ca = {round(v_ca, 3)} kips\n")
            v_cb = (6 * self.lam * math.sqrt(self.f_c) * b_0 * self.d) / 1000
            self.log.write(f"-> v_cb = {round(v_cb, 3)} kips\n")

            alpha_s = get_alpha_s(self, col_loc)
            self.log.write(f"-> alpha_s = {alpha_s} -----> ")
            v_cc = ((((alpha_s * self.d) / b_0) + 2) * self.lam *
                    math.sqrt(self.f_c) * b_0 * self.d) / 1000
            self.log.write(f"v_cc = {round(v_cc, 3)} kips\n")

            use = min(v_ca, v_cb, v_cc)

            self.log.write(f"-> Use V_c = {round(use, 3)} kips\n")

            return use

        self.log.write("Check two-way shear...\n")

        v_u = get_v_u(self, width, q_u, area)  # kip
        phi_vn = get_phi_vn(self, width, col_loc)  # kip

        while phi_vn < v_u:
            self.h += 1 / 12
            self.log.write(
                f"\t{phi_vn} < {v_u} ----> try footing thickness = {round(self.h,3)}\n\t"
            )
            self.set_d("colmumn")
            v_u = get_v_u(self, width, q_u, area)  # kip
            phi_vn = get_phi_vn(self, width, col_loc)  # kip

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            self.log.write(
                f"\t{phi_vn} >> {v_u} ----> try footing thickness = {round(self.h,3)}\n\t"
            )
            self.set_d("colmumn")
            v_u = get_v_u(self, width, q_u, area)  # kip
            phi_vn = get_phi_vn(self, width, col_loc)  # kip

        self.log.write(
            f"-> phi_V_n = {round(phi_vn,3)} > V_u = {round(v_u, 3)} (O.K.)\n")

    def check_one_way_shear(self, q_u, col_size):
        """Checks one-way (beam) shear for column footing, and adjusts
        footing thickness as needed.

        Parameters
        ----------
        q_u : float
            the factored soil pressure in ksf
        col_size : float
            the column width in inches

        """

        self.log.write("Check one-way shear...\n")

        def get_v_u(self, q_u, col_size):
            """Returns the required shear strength (V_u) in kips.

            V_u is taken with critical section at a distance equal to
            the effective dephth, d, away from the face of the wall.
            See ACI 318-14 Sec 9.4.3.2
            """

            self.log.write("Calculate V_u for one-way shear...\n")
            v_u = (q_u * self.width * ((self.length - (col_size / 12)) / 2 -
                                       (self.d / 12)))
            self.log.write(f"-> V_u = {round(v_u, 3)} kips\n")

            return v_u

        def get_phi_vn(self):
            """Returns the factored concrete nominal shear strength (phi_vn)"""

            v_c = (2 * self.lam * math.sqrt(self.f_c) *
                   (self.width * 12) * self.d) / 1000
            self.log.write("Calculate V_c for one-way shear...\n")
            self.log.write(f"-> V_c = {round(v_c, 3)} kips\n")
            phi_vn = 0.75 * v_c
            self.log.write("Calculate phi_V_n for one-way shear...\n")
            self.log.write(f"-> phi_V_n = {round(phi_vn, 3)} kips\n")

            return phi_vn

        v_u = get_v_u(self, q_u, col_size)  # kip
        phi_vn = get_phi_vn(self)  # kip

        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12
            self.log.write(
                f"-> {round(phi_vn,3)} >> {round(v_u, 3)} -----> try footing thickness = {round(self.h,3)} ft\n"
            )
            self.set_d(self.h, "column")
            v_u = get_v_u(self, q_u, col_size)  # kip
            phi_vn = get_phi_vn(self)  # kip

        if phi_vn < v_u:
            self.d = self.round_up_to_precision(
                (v_u * 1000 / (2 * self.lam * 0.75 * math.sqrt(self.f_c) *
                               self.width * 12)),
                0.5,
            )  # in.
            self.log.write(
                f"-> {round(phi_vn, 3)} < {round(v_u, 3)} -----> solve for d. New d = {round(self.d,3)} in.\n"
            )
            self.h = (self.d + 3 + (8 / 8)) / 12
            phi_vn = get_phi_vn(self)  # kip

        self.log.write(
            f"-> phi_V_n = {round(phi_vn,3)} kips > V_u = {round(v_u, 3)} kips (O.K.)\n"
        )

    def get_steel_reqd(self, q_u, l, w):
        """Calculates bending moment and reinforcement ratio. Returns required steel area

        Parameters
        ----------
        q_u : float
            the factored soil pressure in ksf
        col_width : float
            column width in inches
        l : float
            critical length along which q_u is acting
        w : float
            width along which q_u is acting
        """

        m_u = (q_u * w * l**2) / 2
        self.log.write("Calculate required steel reinforcing area...\n")
        self.log.write("Calculate M_u...\n")
        self.log.write(f"-> Critical length, l = {l} ft\n")
        self.log.write(f"-> M_u = {round(m_u, 3)} kip-ft\n")
        k_bar = self.get_k_bar(m_u, 0.9, w * 12)
        rho = self.solve_for_rho(k_bar)
        reqd_area = self.calc_reqd_steel(rho, w * 12, "column")

        return reqd_area

    def get_ftng_dict(self):
        """ """
        d = {
            "id": self.name,
            "ftng_dimensions": f"{self.length} ft x {self.width} ft",
            "ftng_depth": f"{round(self.h, 3)} ft",
            "min_steel_in_long_dim":
            f"{round(self.min_steel_area_length, 3)} sq in",
            "min_steel_in_short_dim":
            f"{round(self.min_steel_area_width, 3)} sq in",
        }

        return d

    def __str__(self):
        """ """
        return f"Footing dimensions: {self.length} ft x {self.width} ft\nDepth: {round(self.h, 2)} ft\nMinimum Required Steel Along {self.length} ft Direction: {round(self.min_steel_area_length, 2)} sqin\nMinimum Required Steel Along {self.width} ft Direction: {round(self.min_steel_area_width, 2)} sqin"
