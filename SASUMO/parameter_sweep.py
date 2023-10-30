# from SASUMO.SASUMO.functions.function import
import os
from itertools import product
import time

import numpy as np
# external imports

from SASUMO.creator import SASUMO
from SASUMO.utils import constants as c
# internal imports
from SASUMO.utils import sobol_first_order


class ParameterSweep(SASUMO):
    def __init__(self, yaml_file_path: str) -> None:

        super().__init__(yaml_file_path)

    def _generate_samples(
        self,
    ) -> np.array:
        if self._settings.get("mode") == "saltelli":
            samples = self._sobol_sequence()

        else:
            n_each = self._settings.get("N")

            samples = [
                eval(var.get("gen_function"))(var)
                if var.get("gen_function", "")
                else np.linspace(**var.distribution.params)
                for _, var in self._settings.get("Variables", {}).items()
            ]

            samples = list(product(*samples)) * n_each
            samples = np.array(samples)

        print(f"Running {len(samples)} simulations")

        np.savetxt(
            os.path.join(self._settings.Metadata.output, c.SAMPLES_FILE_NAME),
            samples,
        )

        return samples


    def _sobol_sequence(self, *args, **kwargs) -> None:
        return sobol_first_order(
            self._problem,
            int(self._settings.get("N")),
            int(time.time())
        )


    def save_results(self, sobol_analysis: list, results: list) -> None:

        pass


    def analyze(self, *args, **kwargs) -> None:

        pass
