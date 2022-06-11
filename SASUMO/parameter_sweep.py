# from SASUMO.SASUMO.functions.function import
import os
import pickle
import sys
import random
import json5 as json
from typing import List, Tuple
from itertools import product

import ray
import click
import numpy as np
from copy import deepcopy

# internal imports
from SASUMO.params import SASUMOConf
from SASUMO.utils import beefy_import, create_folder
from SASUMO.creator import SASUMO

# external imports
from SALib.analyze import sobol
from SALib.sample import saltelli


# TODO organize this somewhere
SEED = 1e6
PROBLEM_DESCRIPT_FILE_NAME = "SALib_Problem.json"
SAMPLES_FILE_NAME = "SALib_Samples.txt"
RESULTS_NAME = "output.txt"
SOBOL_ANALYSIS = lambda x: f"sobol_analysis_{x}.csv"


class ParameterSweep(SASUMO):
    def __init__(self, yaml_file_path: str) -> None:

        super().__init__(yaml_file_path)

    def _generate_samples(
        self,
    ) -> np.array:

        # sample = saltelli.sample(
        # self._problem,
        # self._settings.SensitivityAnalysis.N,
        # calc_second_order = (self._settings.SensitivityAnalysis.calc_second_order,)
        # )

        n_each = self._settings.get("N")

        samples = [
            np.linspace(**var.distribution.params)
            for _, var in self._settings.get("Variables", {}).items()
        ]
        samples = list(product(*samples)) * n_each
        samples = np.array(samples)

        print(f"Running {len(samples)} simulations")

        np.savetxt(
            os.path.join(self._settings.Metadata.output, SAMPLES_FILE_NAME),
            samples,
        )

        return samples

    def _compose_problem(
        self,
    ) -> dict:
        # Including this exclusively so that it is compatiable with the super class. We don't need a problem statement
        return {}

    def _save_problem(
        self,
    ) -> None:
        pass

    def main(self, smoke_test=False) -> List[List[float]]:

        dispatch = []
        results = []

        # dispatch = [(i, self._spawn_process(i)) for i in range(self._settings.sensitivity_analysis.num_runs)]
        for i, _ in enumerate((range(2),) * 2 if smoke_test else self._samples):

            dispatch.append([i, self._spawn_process(i)])

            while len(dispatch) >= self._settings.get("parallel_trials") or (
                i >= (len(self._samples) - 1) and dispatch
            ):

                finished, _ = ray.wait(
                    [_id for _, _id in dispatch], num_returns=1, timeout=0.1
                )

                if len(finished):
                    j = 0
                    while dispatch[j][-1] != finished[0]:
                        j += 1
                    results.append(
                        [ray.get(dispatch[j][1]), dispatch.pop(j)[0]]
                    )  # results.append([[ray.get(_id), i] for i, _id in dispatch])

        return results

    def _spawn_process(self, index: int) -> ray.ObjectRef:

        p = self._f.remote(
            self._settings.generate_process(
                process_var=self._samples[index],
                process_id=str(index),
                random_seed=self._generate_seed(),
            )
        )
        # )
        return p.run.remote()

    def debug_main(
        self,
    ) -> None:

        index = 0

        self._f(
            yaml_params=self._settings.generate_process(
                process_var=self._samples[index],
                process_id=str(index),
                random_seed=self._generate_seed(),
            ),
        ).run()

    def save_results(self, sobol_analysis: list, results: list) -> None:

        # save the results
        np.savetxt(
            os.path.join(self._settings.Metadata.output, RESULTS_NAME),
            np.array(results),
        )

    def analyze(self, *args, **kwargs) -> None:

        pass


@click.command()
@click.option(
    "--debug", is_flag=True, help="Run without Ray. For debugging simulations"
)
@click.option(
    "--smoke-test", is_flag=True, help="Run with Ray but for debugging simulations"
)
@click.option(
    "--finish-existing",
    is_flag=True,
    help="Finish a sensitivity analysis that quit for some reason. It will replay the last # - CPU * 2, just to be safe",
)
@click.argument("settings_file")
def run(debug, smoke_test, finish_existing, settings_file):

    s = ParameterSweep(settings_file)

    if debug:
        if "Remote" in s._settings.get("ManagerFunction").module:
            s._settings.get("ManagerFunction").module = s._settings.get("ManagerFunction").module.replace(
                "Remote", ""
            )
            s.main_fn_helper(s._settings.get("ManagerFunction").module)
        s.debug_main()
    else:
        try:
            ray.init(address="auto")
        except (ConnectionError, RuntimeError):
            print("Starting Ray from python instead")
            # if smoke_test:
            # ray.init(local_mode=smoke_test)
            ray.init()

        results = s.main()

        analysis = s.analyze(results)

        s.save_results(analysis, results)


if __name__ == "__main__":

    run()
