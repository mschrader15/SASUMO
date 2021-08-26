# from SASUMO.SASUMO.functions.function import 
import os
import sys
import ray
import click
import random
import importlib
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


SEED = 1e6

# @click('--settings', help='path to the SASUMO settings file')
class SASUMO:

    def __init__(self, yaml_file_path: str) -> None:
        # instantate the Settings4SASUMO class
        self._settings = Settings4SASUMO(yaml_file_path)
        # save the settings to the new working folder
        self._settings.sensitivity_analysis.working_root = self._create_working_folder()

        self._settings.save_myself(self._settings.sensitivity_analysis.working_root)

        self._problem = self._compose_problem()
        self._samples = self._generate_samples()

        # add the required paths to PYTHON PATH
        self._update_path()

        # import the desired module
        self._f: BaseSUMOFunc = beefy_import(self._settings.simulation_core.manager_function.module)

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

        return saltelli.sample(
                    self._problem,
                    self._settings.sensitivity_analysis.num_runs,
                    calc_second_order=False,
                )


    def _compose_problem(self, ) -> dict:
        return {
            'num_vars': self._settings.sensitivity_analysis.variable_num,
            'names': self._settings.sensitivity_analysis.names,
            'bounds': [var.distribution.bounds 
                for var in self._settings.sensitivity_analysis.variables
            ]
        } 

    def main(self, ) -> dict:
        dispatch = []
        results = []
        for i in range(self._settings.sensitivity_analysis.num_runs):
            
            dispatch.append([i, self._spawn_process(i)])
            
            while (
                len(dispatch) >= self._settings.simulation_core.cpu_cores
                or (i >= (self._settings.sensitivity_analysis.num_runs - 1)
                and dispatch)
            ):

                finished, _ = ray.wait([_id for _, _id in dispatch], num_returns=1, timeout=0.1)

                if len(finished):
                    j = 0
                    while dispatch[j][-1] != finished[0]:
                        j += 1
                    results.append([ray.get(dispatch[j][1]), dispatch.pop(j)[0]])

        finished, _ = ray.wait([_id for _, _id in dispatch], num_returns=len(dispatch))

        results.append([[ray.get(_id), _id] for _id in finished])

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
    # def _create_individual_run_settings(self, index: int):
    #     sample = self._samples[index]
        




if __name__ == "__main__":

    import os
    ROOT = os.path.dirname(os.path.abspath(__file__))
    s = SASUMO(os.path.join(ROOT, '../', 'input_files', 'test.yaml'))

    s.main()
    
# if __name__ == "__main__":

#     ROOT