import math
from types import FunctionType


def _try_eval(val: str) -> float:
    try:
        return eval(val)
    except TypeError:
        return val

def uniform(val: float, width: float, lb: float, ub: float, *args, **kwargs) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the center of the uniform distribution
        width (float): the width of the distribution
        lb (float): min
        ub (float): max
    """
    l = [val, width, lb, ub] 
    for i, arg in enumerate(l):
        if type(arg) is not float:
            l[i] = _try_eval(arg)
    l[1] /= 2
    uniform = [max(min(mult * l[1] + l[0], l[-1]), l[2]) for mult in [-1, 1]]
    return f"uniform({uniform[0]},{uniform[1]})"


def lognormal(val: float, sd: float, lb: float, ub: float, *args, **kwargs) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the average of the lognormal distribution (mu)
        sd (float): the standard deviation of the lognormal distribution 
        lb (float): min
        ub (float): max
    """
    # probably shouldn't have to check like this, but the mean of the distribution should 
    # not be less than the lb or greater than the ub
    l = [val, sd, lb, ub] 
    for i, arg in enumerate(l):
        if type(arg) is not float:
            l[i] = _try_eval(arg)
    val = max(min(l[0], l[-1]), l[2])
    return f"lognormal({l[0]},{l[1]});[{l[2]}, {l[3]}]"

def normal(val: float, sd: float, lb: float, ub: float) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the average of the normal distribution (mu)
        sd (float): the standard deviation of the normal distribution 
        lb (float): min
        ub (float): max
    """
    l = [val, sd, lb, ub] 
    for i, arg in enumerate(l):
        if type(arg) is not float:
            l[i] = _try_eval(arg)
    val = max(min(l[0], l[-1]), l[2])
    return f"normal({l[0]},{l[1]});[{l[2]}, {l[3]}]"



def create_distribution(type: str) -> FunctionType:
    return {
        "uniform": uniform,
        "normal": normal,
        "lognormal": lognormal,
    }[type]