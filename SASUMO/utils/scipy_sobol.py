import numpy as np
from scipy.stats.qmc import Sobol, scale
from SALib.util import scale_samples



def sobol_first_order(problem, num_samples, seed=None):
    """
    Returns the first order Sobol sequence for the given dimension.

    This is only for random simulations, not for Sobol Sensitivity Analysis.
    """
    sobol = Sobol(problem["num_vars"], scramble=True, seed=int(seed))

    # print warning if the number of samples is not a power of 2
    if num_samples and (num_samples & (num_samples - 1) != 0):
        print("Warning: Number of samples is not a power of 2. This will "
              "affect the Sobol sequence.")
    

    sample = sobol.random(num_samples)

    # piggy backing on SALib's scale function
    return scale_samples(sample, problem)

