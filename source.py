import math


class Footing:
    """
    A class used to represent a reinforced concrete footing.
    This is the base (or parent) class for WallFooting and
    ColumnFooting classes.

    This base class contains general varaiables and functions for
    reinforced concrete footings. The subclasses WallFooting and ColumnFooting
    contain specific variables and functions that pertain to their respective
    footing types only.

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
    h : float
        total footing depth in ft
    d : float
        effective depth of footing in inches

    Methods
    ------
    TO DO...

    """

    def __init__(self, name, log, f_c, w_c, conc_type, grade, ftng_type):
        """ This is the constructor for Footing class.

        Parameters
        ----------
        name : str
            footing identifier
        log : _io.TextIOWrapper
            output file for design process steps
        f_c : float
            concrete compressive strength in psi
        w_c : float
            conrete density in pcf
        conc_type : str
            concrete type (normal weight, lightweight, or sand_lightweight)
        grade : int
            reinforcinfg steel grade designation
        ftng_type : str
            footing typr (wall or column)

        """

        self.name = name
        self.log = log
        self.f_c = f_c  # psi
        self.w_c = w_c  # pcf
        self.lam = self.set_lam(conc_type)  # modification factor lambda
        self.beta_1 = self.set_beta_1()
        self.f_y, self.epsilon_y = self.get_steel_props(grade)

        # assume footing intial depth and set effective depth
        if ftng_type == "wall":
            self.h = 1.5  # ft
            self.set_d("wall")  # in
        elif ftng_type == "column":
            self.h = 2
            self.set_d("column")

    def set_lam(self, conc_type):
        """Finds the modification factor "lambda".

        To account for properties of lightweight concrete, a modification factor
        "lambda" is used as a multiplier for sqrt(f_c).
        See ACI 318-14 Sec 19.2.4.1 and 19.2.4.2.

        Parameters
        ----------
        conc_type : str
            Type of concrete - Normal weight ("nw"), Lightweight ("lw")
            or sand-lightweight ("s_lw")

        Returns
        -------
        float
            a float under up to 1.0

        """

        if conc_type == "nw":
            lam = 1.0
        elif conc_type == "lw":
            lam = 0.75
        elif conc_type == "s_lw":
            lam = 0.85

        self.log.write(
            f"Get lambda (ACI 318-14 Sec 19.2.4.2)...\n-> lambda = {lam} for {conc_type} concrete\n")

        return lam

    def set_beta_1(self):
        """Finds the facror beta_1.

        beta_1 is a  factor that is a function of the strength of the concrete.
        See ACI 318-14 Sec 22.2.2.4.3

        Returns
        -------
        float
            a float up to 1.0
        """

        if self.f_c > 4000:
            eq = 0.85 - (0.05 * (self.f_c - 4000) / 1000)
            beta_1 = max(eq, 0.65)
        else:
            beta_1 = 0.85

        self.log.write(
            f"Calulate beta_1 (ACI 318-14 Sec 22.2.2.4.3)...\n-> f-prime-c is {self.f_c} -----> beta_1 = {beta_1}\n")

        return beta_1

    def get_steel_props(self, grade):
        """Gets two reinforcing steel properties.

        The properties are f_y : yield strength in psi; epsilon_y : yield strain

        Parameters
        ----------
        grade : int
            reinforcinfg steel grade designation

        Returns
        --------
        tuple
            (float, float) = (yield strength in psi, yield strain)

        """

        if grade == 40:
            f_y, epsilon_y = (40000, 0.00138)
        elif grade == 60:
            f_y, epsilon_y = (60000, 0.00207)
        elif grade == 75:
            f_y, epsilon_y = (75000, 0.00259)

        self.log.write(
            f"Get properties for Grade {grade} reinforcing steel...\n-> f_y = {f_y} psi, epsilon_y = {epsilon_y}\n")

        return f_y, epsilon_y

    def set_d(self, ftng_type, bar_size=8):
        """Calculates the footing's effective depth "d" in inches.

        "d" is the centroid of the reinforcing steel bars. For a good approximation,
        a bar size diameter of 8 inches is assumed for a defualt value.

        Parameters
        ----------
        ftng_type : str
            describes footing type - wall or column
        bar_size : int
            number of bar (default is #8)

        Returns
        -------
        flaot
            the effective depth "d" in inches
        """

        if ftng_type == "wall":
            # d = h - cover - bar-diameter / 2
            self.d = (self.h * 12) - 3 - ((bar_size / 8) / 2)
        else:
            # d = h - cover - bar-diameter
            self.d = (self.h * 12) - 3 - (bar_size / 8)

        self.log.write(
            f"Caluclate d for footing thickness h = {round(self.h, 3)} ft...\n-> d = {round(self.d, 2)} in.\n")

    def net_asp(self, asp, w_e, bottom):
        """Calculates the net allowable soil pressure (ASP) in ksf.

        Paramaters
        ----------
        asp : float
            the total allowable soil pressure in psf
        w_e : int
            the density of the earth in pcf
        bottom : float
            bottom of footing relative to earth surface in feet

        Returns
        -------
        float
            net allowable soil pressure in ksf

        """

        # net ASP = (ASP - weight of earth above footing - weight of footing) / 1000 kips
        net_asp = (asp - (w_e * (bottom - self.h)) -
                   (self.w_c * self.h)) / 1000

        self.log.write("Calculate net allowable soil pressure...\n")
        self.log.write(
            f"-> ASP = {asp} psf, w_e = {w_e} pcf, w_c = {self.w_c} pcf, bottom of footing {bottom} ft below eartth surface.\n")
        self.log.write(f"-> Net allowable soil pressure = {net_asp} ksf.\n")

        return net_asp

    def factored_soil_pressure(self, d_l, l_l, dimension):
        """Calculates factored soil pressure to be used for footing design.

        The factored soil pressure is calculated using factors found
        in ACI 318-14 Sec 5.3.1 equation b.

        Parameters
        ----------
        d_l : float
            service dead load to be supported
        l_l : float
            service live load to be supported
        dimesion : float
            dimension of footing (width for wall, area for column)

        Returns
        --------
        float
            factored soil pressure in ksf
        """

        factored_asp = ((1.2 * d_l) + (1.6 * l_l)) / dimension

        self.log.write(
            f"Calculate factored soil pressure, q_u...\n-> q_u = {round(factored_asp, 2)} ksf\n")

        return factored_asp

    def get_k_bar(self, m_u, phi, b):
        """Calculates the coefficient of resistance, k_bar

        Parameters
        ----------
        m_u : float
            bending moment
        phi : float
            strength reduction factor (ACI 318-14 Sec 21.2)
        b : float
            element width

        Returns
        -------
        float
            the coefficient of resistance, k_bar

        """

        k_bar = m_u * 12 / (phi * b * (self.d**2))

        self.log.write(f"-> k_bar = {round(k_bar, 4)} ksi -----> ")

        return k_bar

    def solve_for_rho(self, k_bar):
        """Calculates reinforcement ratio (rho)

        The process includes calculating rho from given k_bar value
        and checking if phi is value assumed (0.9). If it isn't, k_bar
        is recalculated as well as the correct value for rho.

        Parameters
        ----------
        k_bar : float
            coefficient of resistance

        Rteurns
        -------
        float
            reinforcement ratio (rho) rounded up to nearest one ten-thousandth
        """

        # the following combines and converts two equations to solve for rho
        # the eqs can be found in "Reinforced Concrete Design" by Abi Aghayere (p. 32)
        a = (-0.59 * (self.f_y**2)) / self.f_c
        b = self.f_y
        c = -k_bar * 1000  # multiply by 1000 so k_bar in psi
        rho = (-b + math.sqrt((b**2) - (4 * a * c))) / \
            (2 * a)  # positive variation of quadratic equation

        self.log.write(f"rho = {self.round_up(rho, 4)}\n")
        self.log.write(f"Check assumption that phi = 0.9...\n")

        phi = self.get_phi(rho)

        if phi < 0.9:
            k_bar = self.get_k_bar(m_u, phi, b)
            c = -k_bar * 1000
            rho = (-b + math.sqrt((b**2) - (4 * a * c))) / (2 * a)

            self.log.write(f"-> phi = {phi} < 0.9. Recalculate k_bar...\n")
            self.log.write(f"-> rho = {self.round_up(rho, 4)}\n")

        return self.round_up(rho, 4)

    def get_phi(self, rho):
        """Calculates strength reduction factor, phi

        The values of phi are taken from ACI 318-14 Sec 21.2.2

        Parameters
        ----------
        rho : float
            reinforcement ratio

        Returns
        -------
        float
            strength reduction factor, phi
        """

        # eq 2-2 in "Reinforced Concrete Design" by Abi Aghayere (p. 32)
        epsilon_t = (0.002555 * self.f_c * self.beta_1 /
                     (rho * self.f_y)) - 0.003

        if epsilon_t <= self.epsilon_y:
            self.log.write("-> Compression section -----> ")
            phi = 0.65
        elif epsilon_t >= 0.005:
            self.log.write("-> Tension section -----> ")
            phi = 0.9
        else:
            self.log.write(f"-> Transition section -----> ")
            phi = 0.65 + \
                ((0.25 * (epsilon_t - self.epsilon_y) / (0.005 - self.epsilon_y)))

        self.log.write(f"phi = {round(phi, 2)}\n")

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

        Returns
        --------
        float
            amount of steel required by analysis in square inches
        """
        # eq found in "Reinforced Concrete Design" by Abi Aghayere (p. 32)
        reqd_area = rho * b * self.d

        self.log.write(
            "Calculate required steel area (ACI 318-14 Sec 9.6.1.1)...\n")

        if ftng_type == "wall":
            self.log.write(
                f"-> A_s required = {round(reqd_area, 3)} sq_in per foot of wall\n")
        else:
            self.log.write(f"-> A_s required = {round(reqd_area, 3)} sq_in\n")

        return reqd_area

    def get_min_beam(self, b):
        """Calculates the minimum flexural reinforcement for nonprestressed beams

        See ACI Section 9.6.1.2

        Parameters
        ----------
        b : float
            element width in inches

        Returns
        -------
        float
            minimum flexural reinforcement for nonprestressed beams in square inches
        """

        a = (3 * math.sqrt(self.f_c) / self.f_y) * b * self.d
        b = (200 / self.f_y) * b * self.d
        min_area_beam = max(a, b)

        self.log.write(
            f"Calculate A_s,min for beams (ACI 318-14 Sec 9.6.1.2)...\n-> A_s,min for beams = {round(min_area_beam,3)} sq in.\n")

        return min_area_beam

    def get_min_slab(self, b):
        """Calculates the minimum flexural reinforcement for slabs

        See ACI Section 7.6.1.1

        Parameters
        ----------
        b : float
            element width in inches

        Returns
        -------
        float
            the minimum flexural reinforcement for slabs in square inches
        """

        if self.f_y < 60000:
            # multiply by 12 to convert h to inches
            min_are_slab = 0.0020 * b * self.h * 12
        else:
            a = ((0.0018 * 60000) / self.f_y) * b * self.h * 12
            b = 0.0014 * b * self.h * 12
            min_area_slab = max(a, b)

        self.log.write(
            f"Calculate A_s,min for slabs (ACI 318-14 Sec 7.6.1.1)...\n-> A_s,min for slabs = {round(min_area_slab,3)} sq in.\n")

        return min_area_slab

    def four_thirds_reqd(self, reqd_area):
        """Calculates 1.33 x reqd_area

        If A_s_provided is at least one-third greater than A_s_required by Sec 9.6.1.1,
        then 9.6.1.2 need not be satisfied. See ACI 318-14 Sec 9.6.1.3

        Parameters
        ----------
        reqd_area : float
            area of steel required by analysis (ACI 318-14 Sec 9.6.1.1)

        Returns
        --------
        float
            1.33 x given reqd_area
        """

        sec_9_6_1_3 = (4 / 3) * reqd_area

        self.log.write(
            f"Calculate 1.33 x A_s required (ACI 318-14 Sec 9.6.1.3)...\n-> A_s as required by 9.6.1.3 = {round(sec_9_6_1_3, 3)} sq in.\n")

        return sec_9_6_1_3

    def get_min_reinforcing(self, b, reqd_area):
        """Calculates the governing minimum required steel for footing

        The minimum steel required is the maximum of A_s,min for beams, A_s,min
        for slabs, and A_s reqd. Unless as provisioned by ACI 318-14 Sec 9.6.1.3

        Parameters
        ----------
        b : float
            element width
        reqd_area : float
            minimum required steel reinforcement provided by analysis

        Returns
        -------
        float
            governing minimum required steel for footing in square inches
        """
        min_area_beam = self.get_min_beam(b)
        min_area_slab = self.get_min_slab(b)

        if reqd_area >= min_area_beam:
            # no need to check ACI Sec 9.6.1.3
            governing = max(min_area_beam, min_area_slab, reqd_area)
        else:
            # check if ACI Sec 9.6.1.3 allows for smaller steel area
            sec_9_6_1_3 = self.four_thirds_reqd(reqd_area)
            governing = max(min(min_area_beam, sec_9_6_1_3), min_area_slab)

        self.log.write(f"-> Use A_s = {round(governing,3)} sq in.\n")

        return governing

    def round_up_to_precision(self, x, precision):
        """ Rounds given number up to desired precision

        Note that 0.5 is the default precision.
        Example:
        x = 11'-2" (11.1667 ft), precision = 0.3333333.
        Goal -> round up so that 11.xx = 11'-4", 11'-6" (default), 11'-8", 12'-0"
        Returns 11.333 ft (11'-4")

        Parameters
        ----------
        x : float
            number to be rounded
        precision : float
            desired precision to round up to (a float under 1)

        Returns
        --------
        float
            x rounded up to desired precision

        """
        # first get ceiling of x
        ceil = math.ceil(x)
        temp1 = ceil
        temp2 = ceil

        # round x up to nearest 0.5
        if (temp1 - x) > 0.5:
            temp1 -= 0.5

        # round x up to nearest precision
        while (temp2 - x) > precision:
            temp2 -= precision

        # return the minimum of the two rounded values
        return min(temp1, temp2)

    def round_up(self, x, n):
        """ Rounds number up to 10**-n decimal

        Parameters
        ----------
        x : float
            number to be rounded up
        n : int
            decimal to raise 10 to (negatively)

        Returns
        -------
        float
            x rounded up to 10**-n decimal
        """

        # multiply x by 10 to nth power, ceiling it, then divide back
        return math.ceil(x * 10**n) / (10**n)


class WallFooting(Footing):
    """TO DO...
    """

    def __init__(self, name, log, precision, wall_width, wall_type, d_l, l_l, f_c, grade, a_s_p, bottom, conc_type, w_c, w_e,):
        """TO DO...
        """
        super().__init__(name, log, f_c, w_c, conc_type, grade, "wall")
        self.width = 0
        self.min_steel_area = 0

        self.design_wall_footing(
            precision, wall_width, wall_type, d_l, l_l, a_s_p, bottom, w_e)

    def design_wall_footing(self, precision, wall_width, wall_type, d_l, l_l, a_s_p, bottom, w_e,):
        """ Designs wall footing parameters and checks adequacy

        Parameters
        ----------
        precision : float
            precsion to round up to in footing design
        wall_width : float
            width of wall in inches
        wall_type : str
            type of wall (concrete or masonry)
        d_l : float
            dead load in kips/ft
        l_l : float
            live load in kips/ft
        a_s_p : float
            allowable soil pressure in psi
        bottom : float
            bottom of footing relative to earth surface
        w_e : float
            density of earth in pcf
        """

        # get footing width in ft
        self.width = self.get_req_width(d_l, l_l,
                                        a_s_p, w_e, bottom, precision)
        # get factored soil pressure ksf
        q_u = self.factored_soil_pressure(d_l, l_l, self.width)
        # check footing thickness is adequate for one-way-shear
        self.check_one_way_shear(q_u, self.width, wall_width)
        # get required steel area by analysis
        steel_reqd = self.get_steel_reqd(q_u, wall_width, wall_type)
        # get minimum required steel are according to ACI
        self.min_steel_area = self.get_min_reinforcing(12, steel_reqd)

    def get_req_width(self, d_l, l_l, a_s_p, w_e, bottom, precision):
        """Calculates net allowable soil pressure, and required
        width of wall footing, rounded up to desired precision.

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

        Returns
        -------
        float
            design width of footing in ft

        """

        # calculate net allowable soil pressure
        net_asp = self.net_asp(a_s_p, w_e, bottom)
        # calculate req'd footing width based on net_asp
        reqd_width = (d_l + l_l) / net_asp
        # use width rounded up to desired precision
        used_width = self.round_up_to_precision(reqd_width, precision)

        self.log.write(
            f"Calculate required footing width:\n-> Required footing width: {round(reqd_width, 2)} ft.\n-> Use {round(used_width, 3)} ft\n")

        return used_width

    def check_one_way_shear(self, q_u, req_width, wall_width):
        """Checks one-way (beam) shear for wall footing, and adjusts
        footing thickness as needed.

        Parameters
        ----------
        q_u : float
            factored soil pressure in ksf
        req_width : float
            width of footing in ft
        wall_width : float
            width of wall in inches

        """

        def get_v_u(self, q_u, req_width, wall_width):
            # Returns the required shear strength (V_u) in kips / ft of wall.

            # V_u is taken with critical section at a distance equal to
            # the effective depth, d, away from the face of the wall.
            # See ACI 318-14 Sec 9.4.3.2

            v_u = q_u * (((req_width - (wall_width / 12)) / 2) - (self.d / 12))

            self.log.write(
                f"Calculate V_u for one-way shear...\n-> V_u = {round(v_u, 3)} kips /ft of wall\n")

            return v_u

        def get_phi_vn(self):
            # Returns the factored concrete nominal shear strength (phi_vn)

            # v_c = 2 * lamba * sqrt(f_c) * b * d -> phi_vn = 0.75 * v_c
            phi_vn = 0.75 * (2 * self.lam * math.sqrt(self.f_c)
                             * 12 * self.d) / 1000
            self.log.write(
                f"Calculate phi_V_n for one-way shear...\n-> phi_V_n = {round(phi_vn, 3)} kips /ft of wall\n")

            return phi_vn

        self.log.write("Check one-way shear...\n")

        # get required shear strength in kip/ft
        v_u = get_v_u(self, q_u, req_width, wall_width)
        # get factored nominal shear strength pf conrete in kip/ft
        phi_vn = get_phi_vn(self)

        # adjust footing depth if shear strength is >> shear req'd
        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12  # minus an inch of thickness
            self.log.write(
                f"-> phi_V_n = {round(phi_vn,3)} >> V_u = {round(v_u, 3)} -----> try footing thickness = {round(self.h,3)} ft\n")
            self.set_d("wall")  # adjust d accordingly
            # get new shear/shear-strength values
            v_u = get_v_u(self, q_u, req_width, wall_width)
            phi_vn = get_phi_vn(self)

        # adjust footing depth if shear strength is < shear req'd
        if phi_vn < v_u:
            # solve for d from v_c equation
            self.d = self.round_up_to_precision(
                (v_u * 1000 / (2 * self.lam * 0.75 * math.sqrt(self.f_c) * 12)))
            # adjust thickness accordingly
            self.h = (self.d + 3 + ((8 / 8) / 2)) / 12
            self.log.write(
                f"-> phi_V_n = {round(phi_vn,3)} < V_u = {round(v_u, 3)} -----> try footing thickness = {round(self.h,3)} ft\n")
            # get new shear strength
            phi_vn = get_phi_vn(self)

        self.log.write(
            f"-> phi_V_n = {round(phi_vn,3)} > V_u = {round(v_u, 3)} (O.K.)\n")

    def get_steel_reqd(self, q_u, wall_width, wall_type):
        """Calculates bending moment and reinforcement ratio

        Parameters
        ----------
        q_u : float
            the factored soil pressure in ksf
        wall_width : float
            the wall width in inches
        wall_type : str
            wall type (masonry or concrete)

        Returns
        -------
        float
            required steel area

        """

        # set critical length based on wall type
        if wall_type == "masonry":
            l = (self.width - (wall_width / 12)) / 2 + (0.25 * wall_width / 12)
        elif wall_type == "concrete":
            l = (self.width - (wall_width / 12)) / 2

        # calculate cantilever beam moment = w(L**2)/2
        m_u = q_u * l**2 / 2

        self.log.write(
            f"Calculate M_u...\n -> {wall_type} wall -----> critical length = {round(l,2)} ft\n-> M_u = {round(m_u,2)} kip-ft\n")

        # get k_bar
        k_bar = self.get_k_bar(m_u, 0.9, 12)
        # get steel ratio
        rho = self.solve_for_rho(k_bar)
        # get req'd steel area by analysis (rho * b * d)
        reqd_area = self.calc_reqd_steel(rho, 12, "wall")

        return reqd_area

    def ftng_dict(self):
        """ Dictionary of final footing design

        Returns
        -------
        dict
            dictionary of final footing design
        """
        d = {
            "id": self.name,
            "ftng_width": f"{round(self.width, 3)} ft",
            "ftng_depth": f"{round(self.h, 3)} ft",
            "min_steel": f"{round(self.min_steel_area, 2)} sq in per ft",
        }

        return d

    def __str__(self):
        return f"\
        Footing width: {round(self.width, 2)} ft\n\
        Depth: {round(self.h, 2)} ft\n\
        Minimum Required Steel: {round(self.min_steel_area, 2)} sqin/ft"


class ColumnFooting(Footing):
    """TO DO...
    """

    def __init__(self, name, log, precision, col_width, d_l, l_l, f_c, grade, a_s_p, bottom, width_restriction, col_loc, conc_type, w_c, w_e):
        """TO DO...
        """
        super().__init__(name, log, f_c, w_c, conc_type, grade, "column")
        self.length = 0
        self.width = 0
        self.min_steel_area_width = 0
        self.min_steel_area_length = 0

        self.design_column_footing(
            precision, col_width, d_l, l_l, a_s_p, bottom, width_restriction, col_loc, w_e)

    def design_column_footing(self, precision, col_width, d_l, l_l, a_s_p, bottom, width_restriction, col_loc, w_e):
        """ Designs wall footing parameters and checks adequacy

        Parameters
        ----------
        precision : float
            precsion to round up to in footing design
        col_width : float
            width of column (square column)
        d_l : float
            dead load in kips/ft
        l_l : float
            live load in kips/ft
        a_s_p : float
            allowable soil pressure in psi
        bottom : float
            bottom of footing relative to earth surface
        width_restriction : float
            maximum width of footing
        col_loc : str
            column location on footing (interior, edge, corner)
        w_e : float
            density of earth in pcf
        """

        # get footing dimensions in ft
        self.length, self.width = self.get_dimensions(
            d_l, l_l, a_s_p, w_e, bottom, width_restriction, precision)
        # get footing area in square ft
        area = self.length * self.width
        # get factored soil pressure in ksf
        q_u = self.factored_soil_pressure(d_l, l_l, area)
        # check adequacy of footing thickness for one-way shear
        self.check_two_way_shear(q_u, area, col_width, col_loc)
        # check adequacy of footing thickness for two-way shear
        self.check_one_way_shear(q_u, col_width)

        # get required steel area for **length** of footing (both dimesnsions if square)

        # get critical length
        l = (self.length - (col_width / 12)) / 2
        # get steel required by analysis
        steel_reqd_length = self.get_steel_reqd(q_u, l, self.width)
        # get minimum steel required by ACI
        self.min_steel_area_length = self.get_min_reinforcing(
            self.width * 12, steel_reqd_length)
        self.min_steel_area_width = self.min_steel_area_length

        if self.width != self.length:
            # get required steel area for **width** of footing
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
        """Calculates footing dimensions required rounded up to desired precision.

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

        Returns
        -------
        tuple
            required footing dimensions (l, w) -> (float, float)

        """

        # first calculate net allowable soil pressure
        net_asp = self.net_asp(a_s_p, w_e, bottom)
        # req'd area base on net_asp
        reqd_area = (d_l + l_l) / net_asp

        self.log.write(
            f"Calculate required footing area...\n-> Required footing area: {round(reqd_area, 2)} square ft\n")

        # if there is a width restriction length will not equal width
        if max_width:
            long_side = self.round_up_to_precision(
                (reqd_area / max_width), precision)
            l, w = (long_side, max_width)
        else:
            side = self.round_up_to_precision(math.sqrt(reqd_area), precision)
            l, w = (side, side)

        actual_area = l * w

        self.log.write(
            f"-> Use: {l} ft x {w} ft\n-> Actual area provided: {actual_area} sq ft\n")

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
            location of column on footing (interior, edge, or corner)
        """

        def get_v_u(self, width, q_u, area):
            # Returns required shear strength (V_u) in kips.

            # V_u is taken with critical section so that its perimeter
            # b_0 does not come closer to the edge of the column than one-half the effective depth.
            # See ACI 318-14 Sec 22.6.4.1

            # get edge length of perimeter b_0 of critical section in inches
            a = width + self.d
            # get required shear strength in kips
            v_u = q_u * (area - ((a / 12)**2))

            self.log.write(
                f"Calculate required shear strenght, V_u (ACI 318-14 Sec 22.6.4.1)...\n-> V_u = {round(v_u,3)} kips\n")

            return v_u

        def get_phi_vn(self, width, col_loc):
            # Returns factored concrete shear strength (phi_V_n) in kips

            # phi_V_n is taken as 75% of concrete shear strangth, V_c.
            # See ACI 318-14 Sec 21.2 and Sec 22.6.5.2

            # get edge length of perimeter b_0 of critical section in inches
            a = width + self.d
            # get perimeter of critical section in inches
            b_0 = 4 * a
            # get concrete shear strength in kip
            v_c = get_v_c(self, b_0, col_loc)
            # get factored nominal concrete shear strength in kip
            phi_vn = 0.75 * v_c
            self.log.write(
                f"Calculate factored concrete shear strength, phi_V_n (ACI 318-14 Sec 21.2)...\n-> phi_V_n = {round(phi_vn, 3)} kips\n")

            return phi_vn

        def get_v_c(self, b_0, col_loc):
            # Returns concrete shear strength V_c
            # See ACI Sec 22.6.5.2
            # b_0 is the perimeter of critical section taken at a distance d/2 from column edge

            def get_alpha_s(self, col_loc):
                # Returns alpha_s
                # See ACI 318-14 Sec 22.6.5.3

                if col_loc == "interior":
                    return 40
                elif col_loc == "edge":
                    return 30
                elif col_loc == "corner":
                    return 20

            # get factor alpha_s for third possible value of v_c (v_cc)
            alpha_s = get_alpha_s(self, col_loc)

            # get all possible values of shear strength
            v_ca = (4 * self.lam * math.sqrt(self.f_c) * b_0 * self.d) / 1000
            v_cb = (6 * self.lam * math.sqrt(self.f_c) * b_0 * self.d) / 1000
            v_cc = ((((alpha_s * self.d) / b_0) + 2) * self.lam *
                    math.sqrt(self.f_c) * b_0 * self.d) / 1000
            # use minimum of above three values
            use = min(v_ca, v_cb, v_cc)

            self.log.write(
                f"Calcukate V_c for two two-way shear (ACI Sec 22.6.5.2)...\n")
            self.log.write(f"-> v_ca = {round(v_ca, 3)} kips\n")
            self.log.write(f"-> v_cb = {round(v_cb, 3)} kips\n")
            self.log.write(f"-> v_cc = {round(v_cc, 3)} kips\n")
            self.log.write(f"-> Use V_c = {round(use, 3)} kips\n")

            return use

        self.log.write("Check two-way shear...\n")

        # get required shear strength in kips
        v_u = get_v_u(self, width, q_u, area)
        # get factored nominal shear shear strength in kips
        phi_vn = get_phi_vn(self, width, col_loc)

        # if shear strength is less than req'd adjust footing thickness
        while phi_vn < v_u:
            self.h += 1 / 12  # add an inch to thickness
            self.log.write(
                f"{phi_vn} < {v_u} ----> try footing thickness = {round(self.h,3)}\n")
            self.set_d("colmumn")  # adjust d accordingly
            v_u = get_v_u(self, width, q_u, area)
            phi_vn = get_phi_vn(self, width, col_loc)

        # if shear strength is >> req'd adjust footing thickness
        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12  # minus an inch to thickness
            self.log.write(
                f"{phi_vn} >> {v_u} ----> try footing thickness = {round(self.h,3)}\n")
            self.set_d("colmumn")  # adjust d accordingly
            v_u = get_v_u(self, width, q_u, area)
            phi_vn = get_phi_vn(self, width, col_loc)

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

        def get_v_u(self, q_u, col_size):
            # Returns the required shear strength (V_u) in kips.

            # V_u is taken with critical section at a distance equal to
            # the effective dephth, d, away from the face of the wall.
            # See ACI 318-14 Sec 9.4.3.2

            v_u = (q_u * self.width *
                   ((self.length - (col_size / 12)) / 2 - (self.d / 12)))
            self.log.write(
                f"Calculate V_u for one-way shear...\n-> V_u = {round(v_u, 3)} kips\n")

            return v_u

        def get_phi_vn(self):
            # Returns the factored concrete nominal shear strength (phi_vn)

            # v_c = 2 * lamba * sqrt(f_c) * b * d -> phi_vn = 0.75 * v_c
            phi_vn = 0.75 * (2 * self.lam * math.sqrt(self.f_c)
                             * (self.width * 12) * self.d) / 1000
            self.log.write(
                f"Calculate phi_V_n for one-way shear...\n-> phi_V_n = {round(phi_vn, 3)} kips\n")

            return phi_vn

        self.log.write("Check one-way shear...\n")
        # get req'd shear strength in kip
        v_u = get_v_u(self, q_u, col_size)
        # get factored concrete shear strength in kip
        phi_vn = get_phi_vn(self)

        # adjust footing depth if shear strength is >> shear req'd
        while phi_vn >= (1.5 * v_u):
            self.h -= 1 / 12  # minus an inch of thickness
            self.log.write(
                f"-> {round(phi_vn,3)} >> {round(v_u, 3)} -----> try footing thickness = {round(self.h,3)} ft\n")
            self.set_d(self.h, "column")  # adjust d accordingly
            v_u = get_v_u(self, q_u, col_size)
            phi_vn = get_phi_vn(self)

        # adjust footing depth if shear strength is < shear req'd
        if phi_vn < v_u:
            # solve for d from v_u
            self.d = self.round_up_to_precision(
                (v_u * 1000 / (2 * self.lam * 0.75 * math.sqrt(self.f_c) * self.width * 12)), 0.5)
            self.h = (self.d + 3 + (8 / 8)) / 12  # calculate h
            self.log.write(
                f"-> {round(phi_vn, 3)} < {round(v_u, 3)} -----> solve for d. New d = {round(self.d,3)} in.\n")
            phi_vn = get_phi_vn(self)

        self.log.write(
            f"-> phi_V_n = {round(phi_vn,3)} kips > V_u = {round(v_u, 3)} kips (O.K.)\n")

    def get_steel_reqd(self, q_u, l, w):
        """Calculates bending moment and reinforcement ratio

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

        Returns
        -------
        float
            required steel area
        """

        # calculate cantilever beam moment = w(L**2)/2
        m_u = (q_u * w * l**2) / 2

        self.log.write(
            f"Calculate required steel reinforcing area...\nCalculate M_u...\n-> Critical length, l = {l} ft\n-> M_u = {round(m_u, 3)} kip-ft\n")

        # get k_bar
        k_bar = self.get_k_bar(m_u, 0.9, w * 12)
        # get steel ration
        rho = self.solve_for_rho(k_bar)
        # get req'd steel area by analysis (rho * b * d)
        reqd_area = self.calc_reqd_steel(rho, w * 12, "column")

        return reqd_area

    def ftng_dict(self):
        """ Dictionary of final footing design

        Returns
        -------
        dict
            dictionary of final footing design
        """
        d = {
            "id": self.name,
            "ftng_dimensions": f"{self.length} ft x {self.width} ft",
            "ftng_depth": f"{round(self.h, 3)} ft",
            "min_steel_in_long_dim": f"{round(self.min_steel_area_length, 3)} sq in",
            "min_steel_in_short_dim": f"{round(self.min_steel_area_width, 3)} sq in",
        }

        return d

    def __str__(self):
        return f"\
        Footing dimensions: {self.length} ft x {self.width} ft\n\
        Depth: {round(self.h, 2)} ft\n\
        Minimum Required Steel Along {self.length} ft Direction: {round(self.min_steel_area_length, 2)} sqin\n\
        Minimum Required Steel Along {self.width} ft Direction: {round(self.min_steel_area_width, 2)} sqin"
