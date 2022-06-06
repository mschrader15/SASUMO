import math
from types import FunctionType



def uniform(val: float, width: float, lb: float, ub: float, *args, **kwargs) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the center of the uniform distribution
        width (float): the width of the distribution
        lb (float): min
        ub (float): max
    """
    
    width /= 2
    uniform = [max(min((mult * width + val), ub), lb) for mult in [-1, 1]]
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
    val = max(min(val, ub), lb)
    return f"lognormal({val},{sd});[{lb}, {ub}]"

def normal(val: float, sd: float, lb: float, ub: float) -> str:
    """
    This generates a uniform distribution

    Args:
        val (float): the average of the normal distribution (mu)
        sd (float): the standard deviation of the normal distribution 
        lb (float): min
        ub (float): max
    """
    # probably shouldn't have to check like this, but the mean of the distribution should 
    # not be less than the lb or greater than the ub 
    val = max(min(val, ub), lb)
    return f"normal({val},{sd});[{lb}, {ub}]"



def create_distribution(type: str) -> FunctionType:
    return {
        "uniform": uniform
    }[type]