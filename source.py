import math


def factor_loads(self, d_l, d_d):
    """ Calculates the minimum design load by multiplying service loads by given factors (ACI Section 5.3.1)
    NOTE: This ACI section is slightly modified for our purpose. See ACI Code, Section 5.3 for more details.
    """

    return (1.6 * d_l) + (1.2 * d_d)


def reqd_area(self, rho, b, d):
    """ Calculates the minimum flexural reinforcement required by analysis (ACI Section 9.6.1.1)

    rho = ratio of tension steel area to effective concrete area
    b = section width
    d = effective depth of steel
    """

    return rho * b * d

def min_area_beams(self, concrete_strength, steel_strength, b, d):
    """ Calculates the minimum flexural reinforcement for nonprestressed beams
    as required by ACI Section 9.6.1.2
    """
    a = (3 * math.sqrt(concrete_strength) / steel_strength) * b * d
    b = (200 / steel_strength) * b * d
    result = max(a, b)

    print('ACI Section 9.6.1.2 - Minimum flexural reinforcement for nonprestressed beams: ', result)

    return result

def net_asp(self, asp, w_e, w_c, h, bottom):
    return asp - (w_e * (bottom - h)) - (w_c * h)


class TestClass:
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return 'number: {}'.format(self.number)