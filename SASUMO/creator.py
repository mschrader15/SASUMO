# from SASUMO.SASUMO.functions.function import
import os
import sys
import random
import json5 as json
import csv
from typing import List

import ray
import click
import numpy as np
from copy import deepcopy
from datetime import datetime

# internal imports
from params import Settings4SASUMO
from params import ProcessParameters
from functions import BaseSUMOFunc
from utils import path_constructor, beefy_import

# external imports
from SALib.analyze import sobol
from SALib.sample import saltelli

# TODO organize this somewhere
SEED = 1e6
PROBLEM_DESCRIPT_FILE_NAME = "SALib_Problem.json"
SAMPLES_FILE_NAME = "SALib_Samples.txt"
RESULTS_NAME = "output.txt"
SOBOL_ANALYSIS = lambda x: f"sobol_analysis_{x}.csv"



# @click('--settings', help='path to the SASUMO settings file')
class SASUMO:

    def __init__(self, yaml_file_path: str) -> None:
        # instantate the Settings4SASUMO class
        self._settings = Settings4SASUMO(yaml_file_path)
        # save the settings to the new working folder
        self._settings.sensitivity_analysis.working_root = self._create_working_folder()
        

        # it should save now because want to preserve the pre-run state. Should it watch and copy a 
        self._settings.save_myself(
            os.path.join(
                self._settings.sensitivity_analysis.working_root,
                # TODO move all these file name constants somewhere else
                "settings.yaml"
            )
        )

        # generate and save the problem definition
        self._problem = self._compose_problem()
        self._save_problem()

        # generate the samples
        self._samples = self._generate_samples()

        # add the required paths to PYTHON PATH
        self._update_path()

        # import the desired module
        self._f = None
        self.main_fn_helper(self._settings.simulation_core.manager_function.module)

    def main_fn_helper(self, module_path: str) -> None:
        """
        This is really just for debug mode. To override the "RemoteEmiss...." 

        Args:
            module_path (str): [description]
        """
        self._f = beefy_import(
            module_path
        )
 

    def _update_path(self, ):

        for new_path in [self._settings.simulation_core.manager_function.path, self._settings.simulation_core.simulation_function.path]:
            if new_path:
                if "${" in new_path:
                    new_path = path_constructor(new_path)
                sys.path.append(new_path)

    @staticmethod
    def _generate_seed():
        return random.randint(a=0, b=SEED)

    def _generate_samples(self, ) -> np.array:
        
        sample = saltelli.sample(
            self._problem,
            self._settings.sensitivity_analysis.N,
            calc_second_order=self._settings.sensitivity_analysis.calc_second_order,
        )

        print(f"Running {len(sample)} simulations")

        np.savetxt(os.path.join(self._settings.sensitivity_analysis.working_root, SAMPLES_FILE_NAME), sample)
        
        return sample

    def _compose_problem(self, ) -> dict:

        return {
            'num_vars': self._settings.sensitivity_analysis.variable_num,
            'names': self._settings.sensitivity_analysis.names,
            'bounds': [var.distribution.bounds
                       for var in self._settings.sensitivity_analysis.variables
                       ]
        }

    def _save_problem(self, ) -> None:

        with open(os.path.join(self._settings.sensitivity_analysis.working_root, PROBLEM_DESCRIPT_FILE_NAME), 'w') as f:
            f.write(
                json.dumps(
                    self._problem
                )
            )

    def main(self, ) -> List[List[float]]:

        dispatch = []
        results = []

        # dispatch = [(i, self._spawn_process(i)) for i in range(self._settings.sensitivity_analysis.num_runs)]
        for i, _ in enumerate(self._samples):

            dispatch.append([i, self._spawn_process(i)])

            while (
                len(dispatch) >= self._settings.simulation_core.cpu_cores
                or (i >= (len(self._samples) - 1)
                    and dispatch)
            ):

                finished, _ = ray.wait(
                    [_id for _, _id in dispatch], num_returns=1, timeout=0.1)

                if len(finished):
                    j = 0
                    while dispatch[j][-1] != finished[0]:
                        j += 1
                    results.append([ray.get(dispatch[j][1]), dispatch.pop(j)[0]])     # results.append([[ray.get(_id), i] for i, _id in dispatch])

        return results

    def _spawn_process(self, index: int) -> ray.ObjectRef:

        p = self._f.remote(yaml_settings=deepcopy(self._settings),
                           sample=self._samples[index],
                           seed=self._generate_seed(),
                           sample_num=index
                           )
        return p.run.remote()

    def _create_working_folder(self, ):
        working_p = os.path.join(
            path_constructor(
                self._settings.sensitivity_analysis.working_root
            ),
            self._settings.metadata.name,
            datetime.now().strftime("%Y_%m_%d-%I_%M_%S")
        )

        os.makedirs(working_p, exist_ok=True)

        return working_p

    def debug_main(self, ) -> None:

        self._f(
            yaml_settings=deepcopy(self._settings),
            sample=self._samples[0],
            seed=self._generate_seed(),
            sample_num=0

        ).run()

    def save_results(self, sobol_analysis: list, results: list) -> None:
        # save the sobol analysis
        for i, result in enumerate(sobol_analysis.to_df()):
            result.to_csv(
                os.path.join(
                    self._settings.sensitivity_analysis.working_root, 
                    SOBOL_ANALYSIS(i)
                )
            )

        # save the results
        np.savetxt(
            os.path.join(self._settings.sensitivity_analysis.working_root, RESULTS_NAME), 
            np.array(results)
        )




@click.command()
@click.option('--debug', is_flag=True, help="Run without Ray. For debugging simulations")
@click.argument('settings_file')
def run(debug, settings_file):

    s = SASUMO(settings_file)

    if debug:
        if 'Remote' in s._settings.simulation_core.manager_function.module:
            s._settings.simulation_core.manager_function.module = s._settings.simulation_core.manager_function.module.replace("Remote", "")
            s.main_fn_helper(s._settings.simulation_core.manager_function.module)
        s.debug_main()
    else:
        try:
            ray.init(address="auto")
        except (ConnectionError, RuntimeError):
            print("Starting Ray from python instead")
            ray.init()

        results = sorted([res for res in s.main() if res], key=lambda x: x[1])

        analysis = sobol.analyze(s._problem, np.array([r[0] for r in results]), print_to_console=True)

        s.save_results(analysis, results)


if __name__ == "__main__":

    run()
# if __name__ == "__main__":

#     ROOT
