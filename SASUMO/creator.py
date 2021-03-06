# from SASUMO.SASUMO.functions.function import
import os
import pickle
import sys
import random
from importlib_metadata import distribution
import json5 as json
from typing import List, Tuple

import ray
import click
import numpy as np
from copy import deepcopy

# internal imports
from SASUMO.params import Config
from SASUMO.utils import beefy_import, create_folder

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
        self._settings = Config(yaml_file_path)

        # try to create the folder to work in.
        create_folder(self._settings.Metadata.output)

        # save a copy of the settings file
        self._settings.to_yaml(
            os.path.join(self._settings.Metadata.output, "sasumo_params.yaml"),
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
        self.main_fn_helper(self._settings.get("ManagerFunction").module)

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
            self._settings.SimulationCore.get("ManagerFunction", {}).get("path", ""),
            self._settings.SimulationCore.SimulationFunction.get("path", ""),
        ]:
            if new_path:
                sys.path.append(new_path)

    def _generate_seed(
        self,
    ):
        # If the random seed is a part of the SA then we don't need them
        if self._settings.get("Variables", {}).get("RandomSeed", ""):
            return None
        return random.randint(a=0, b=SEED)

    def _generate_samples(
        self,
    ) -> np.array:

        if self._settings.SensitivityAnalysis.get("mode", "") == "correlated":
            from SALib.sample import sobol_corr

            sample = sobol_corr.sample(
                self._problem,
                self._settings.SensitivityAnalysis.N,
            )

        else:
            sample = saltelli.sample(
                self._problem,
                self._settings.SensitivityAnalysis.N,
                calc_second_order=self._settings.SensitivityAnalysis.calc_second_order,
            )

        print(f"Running {len(sample)} simulations")

        np.savetxt(
            os.path.join(self._settings.Metadata.output, SAMPLES_FILE_NAME),
            sample,
        )

        return sample

    def _compose_problem(
        self,
    ) -> dict:

        return {
            "num_vars": len(self._settings.SensitivityAnalysis.Variables),
            "names": [
                name
                for name, var in self._settings.SensitivityAnalysis.Variables.items()
            ],
            "bounds": [
                self._compose_bounds(var)
                for var in self._settings.SensitivityAnalysis.Variables.values()
            ],
            **(
                {
                    "distrs": [
                        var.distr
                        for _, var in self._settings.SensitivityAnalysis.Variables.items()
                    ]
                }
                if self._settings.SensitivityAnalysis.get("mode", "") == "correlated"
                else {}
            ),
            **(
                {
                    "corr": [
                        var.corr
                        for _, var in self._settings.SensitivityAnalysis.Variables.items()
                    ]
                }
                if self._settings.SensitivityAnalysis.get("mode", "") == "correlated"
                else {}
            ),
        }

    def _compose_bounds(self, variable_obj: object) -> Tuple[float, float]:
        """
        Used to generate the bounds for the simulation. Can be extended to support categoricals

        Args:
            variable_obj (object): An instance of a

        Returns:
            Tuple[float, float]:
        """
        return (
            variable_obj.distribution.params.get("lb", 0),
            variable_obj.distribution.params.ub,
        )

    def _save_problem(
        self,
    ) -> None:

        with open(
            os.path.join(
                self._settings.Metadata.output,
                PROBLEM_DESCRIPT_FILE_NAME,
            ),
            "w",
        ) as f:
            f.write(
                json.dumps(
                    self._problem,
                    indent=4,
                    quote_keys=True,
                    trailing_commas=False,
                )
            )

    def main(self, smoke_test=False) -> List[List[float]]:

        dispatch = []
        results = []

        # dispatch = [(i, self._spawn_process(i)) for i in range(self._settings.sensitivity_analysis.num_runs)]
        for i, _ in enumerate((range(2),) * 2 if smoke_test else self._samples):

            dispatch.append([i, self._spawn_process(i)])

            while len(
                dispatch
            ) >= self._settings.SensitivityAnalysis.parallel_trials or (
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

        return sorted(results, key=lambda x: x[1])

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
        # save the sobol analysis
        for i, result in enumerate(sobol_analysis.to_df()):
            result.to_csv(
                os.path.join(self._settings.Metadata.output, SOBOL_ANALYSIS(i))
            )

        # save the results
        np.savetxt(
            os.path.join(self._settings.Metadata.output, RESULTS_NAME),
            np.array(results),
        )

    def analyze(self, results) -> dict:
        if self._settings.SensitivityAnalysis.get("mode", "") == "correlated":
            from SALib.analyze import sobol_corr

            return sobol_corr.analyze(
                self._problem,
                np.array([r[0] for r in results]),
                self._settings.SensitivityAnalysis.N
            )
        
        return sobol.analyze(
            self._problem, np.array([r[0] for r in results]), print_to_console=True
        )


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

    s = SASUMO(settings_file)

    if debug:
        if "Remote" in s._settings.get("ManagerFunction").module:
            s._settings.get("ManagerFunction").module = s._settings.get(
                "ManagerFunction"
            ).module.replace("Remote", "")
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
