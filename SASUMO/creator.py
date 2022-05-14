# from SASUMO.SASUMO.functions.function import
import os
import sys
import random
import json5 as json
import csv
from typing import List, Tuple

import ray
import click
import numpy as np
from copy import deepcopy
from datetime import datetime

# internal imports
from params import SASUMOConf
from params import ProcessParameters
from functions import BaseSUMOFunc
from utils import path_constructor, beefy_import, create_folder

# external imports
from SALib.analyze import sobol
from SALib.sample import saltelli


# TODO organize this somewhere
SEED = 1e6
PROBLEM_DESCRIPT_FILE_NAME = "SALib_Problem.json"
SAMPLES_FILE_NAME = "SALib_Samples.txt"
RESULTS_NAME = "output.txt"
SOBOL_ANALYSIS = lambda x: f"sobol_analysis_{x}.csv"


class SASUMO:
    def __init__(self, yaml_file_path: str) -> None:
        # instantate the Settings4SASUMO class
        self._settings = SASUMOConf(yaml_file_path)

        # try to create the folder to work in.
        create_folder(self._settings.Metadata.simulation_root)

        # save a copy of the settings file
        self._settings.to_yaml(
            os.path.join(self._settings.Metadata.simulation_root, "sasumo_params.yaml"),
            resolve=True,
        )

        # generate and save the problem definition
        self._problem = self._compose_problem()
        # TODO: Do I need to do this?
        self._save_problem()

        # generate the samples
        self._samples = self._generate_samples()

        # add the required paths to PYTHON PATH
        self._update_path()

        # import the desired module
        self._f = None
        self.main_fn_helper(self._settings.SensitivityAnalysis.manager_function.module)

    def main_fn_helper(self, module_path: str) -> None:
        """
        This is really just for debug mode. To override the "RemoteEmiss...."

        Args:
            module_path (str): [description]
        """
        self._f = beefy_import(module_path)

    def _update_path(
        self,
    ):

        for new_path in [
            self._settings.SimulationCore.manager_function.get("path", ""),
            self._settings.SimulationCore.simulation_function.get("path", ""),
        ]:
            if new_path:
                sys.path.append(new_path)

    @staticmethod
    def _generate_seed():
        return random.randint(a=0, b=SEED)

    def _generate_samples(
        self,
    ) -> np.array:

        sample = saltelli.sample(
            self._problem,
            self._settings.sensitivity_analysis.N,
            calc_second_order=self._settings.sensitivity_analysis.calc_second_order,
        )

        print(f"Running {len(sample)} simulations")

        np.savetxt(
            os.path.join(
                self._settings.sensitivity_analysis.working_root, SAMPLES_FILE_NAME
            ),
            sample,
        )

        return sample

    def _compose_problem(
        self,
    ) -> dict:

        return {
            "num_vars": len(self._settings.SensitivityAnalysis.Variables),
            "names": [
                var.name
                for var in self._settings.SensitivityAnalysis.Variables.values()
            ],
            "bounds": [
                self._compose_bounds(var)
                for var in self._settings.SensitivityAnalysis.Variables.values()
            ],
        }

    def _compose_bounds(self, variable_obj: object) -> Tuple[float, float]:
        """
        Used to generate the bounds for the simulation. Can be extended to support categoricals

        Args:
            variable_obj (object): An instance of a

        Returns:
            Tuple[float, float]:
        """
        return variable_obj.distribution.min, variable_obj.distribution.max

    def _save_problem(
        self,
    ) -> None:

        with open(
            os.path.join(
                self._settings.sensitivity_analysis.working_root,
                PROBLEM_DESCRIPT_FILE_NAME,
            ),
            "w",
        ) as f:
            f.write(json.dumps(self._problem))

    def main(
        self,
    ) -> List[List[float]]:

        dispatch = []
        results = []

        # dispatch = [(i, self._spawn_process(i)) for i in range(self._settings.sensitivity_analysis.num_runs)]
        for i, _ in enumerate(self._samples):

            dispatch.append([i, self._spawn_process(i)])

            while len(dispatch) >= self._settings.SensitivityAnalysis.cpu_cores or (
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
            yaml_settings=self._settings.generate_process(
                process_var=self._samples[index], process_id=str(index)
            ),
            sample_num=index,
        )
        return p.run.remote()

    def debug_main(
        self,
    ) -> None:

        self._f(
            yaml_settings=deepcopy(self._settings),
            sample=self._samples[0],
            seed=self._generate_seed(),
            sample_num=0,
        ).run()

    def save_results(self, sobol_analysis: list, results: list) -> None:
        # save the sobol analysis
        for i, result in enumerate(sobol_analysis.to_df()):
            result.to_csv(
                os.path.join(
                    self._settings.sensitivity_analysis.working_root, SOBOL_ANALYSIS(i)
                )
            )

        # save the results
        np.savetxt(
            os.path.join(
                self._settings.sensitivity_analysis.working_root, RESULTS_NAME
            ),
            np.array(results),
        )


@click.command()
@click.option(
    "--debug", is_flag=True, help="Run without Ray. For debugging simulations"
)
@click.argument("settings_file")
def run(debug, settings_file):

    s = SASUMO(settings_file)

    if debug:
        if "Remote" in s._settings.simulation_core.manager_function.module:
            s._settings.simulation_core.manager_function.module = (
                s._settings.simulation_core.manager_function.module.replace(
                    "Remote", ""
                )
            )
            s.main_fn_helper(s._settings.simulation_core.manager_function.module)
        s.debug_main()
    else:
        try:
            ray.init(address="auto")
        except (ConnectionError, RuntimeError):
            print("Starting Ray from python instead")
            ray.init()

        results = sorted([res for res in s.main() if res], key=lambda x: x[1])

        analysis = sobol.analyze(
            s._problem, np.array([r[0] for r in results]), print_to_console=True
        )

        s.save_results(analysis, results)


if __name__ == "__main__":

    run()
