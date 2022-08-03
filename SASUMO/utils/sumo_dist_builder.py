import math
from types import FunctionType


def _try_eval(val: str) -> float:
    try:
        return eval(val)
    except TypeError:
        return val

def _process_args(val: float, lb: float, ub: float, sd: float = None, width: float = None,) -> list:
    """
    This processes the arguments passed to the distribution function
    """
    l = [val, sd, lb, ub, width] 
    for i, arg in enumerate(l):
        if arg and (type(arg) is not float):
            l[i] = _try_eval(arg)
    # replace sd with width if sd is not provided
    if l[1] is None:
        l[1] = l[4] / 2
    l[0] = max(min(l[0], l[3]), l[2])
    return l

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


def lognormal(val: float, lb: float, ub: float, sd: float = None, width: float = None, *args, **kwargs) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the average of the lognormal distribution (mu)
        sd (float): the standard deviation of the lognormal distribution 
        lb (float): min
        ub (float): max
    """
    l = _process_args(val, lb, ub, sd, width)

    #  from https://stats.stackexchange.com/a/95506 cause I'm dumb...
    lns = math.sqrt(math.log((l[1] / l[0]) ** 2 + 1)) 
    lnmu = math.log(l[0]) - 0.5 * math.log((l[1] / l[0]) ** 2 + 1)
    return f"lognormal({lnmu},{lns});[{l[2]}, {l[3]}]"

def normal(val: float, lb: float, ub: float, sd: float = None, width: float = None, dist: str = "normal", *args, **kwargs) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the average of the normal distribution (mu)
        sd (float): the standard deviation of the normal distribution 
        lb (float): min
        ub (float): max
    """
    l = _process_args(val, lb, ub, sd, width)
    return f"{dist}({l[0]},{l[1]});[{l[2]}, {l[3]}]"


def create_distribution(type: str) -> FunctionType:
    return {
        "uniform": uniform,
        "normal": normal,
        "lognormal": lognormal,
    }[type]