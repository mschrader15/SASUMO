import ray
import click
import random
import importlib
import numpy as np
from copy import deepcopy

from ray.worker import remote
from utils import Settings4SASUMO
from SALib.analyze import sobol
from SALib.sample import saltelli
from utils import Settings4SASUMO
from params import ProcessParameters
from functions import EmissionsSUMOFunc

SEED = 42


# @click('--settings', help='path to the SASUMO settings file')
@ray.remote
class SASUMO:

    def __init__(self, yaml_file_path: str) -> None:
        self._settings = Settings4SASUMO(yaml_file_path)
        self._problem = self._compose_problem()
        self._samples = self._generate_samples()

        # import the desired module
        self._f: EmissionsSUMOFunc = importlib.import_module(self._settings.simulation_core.function)


    @ray.method(num_returns=1)
    def _f(self, individual_run_settings) -> None:
        """
        Execute the main function. This is pointed to in the input YAML file

        Args:
            individual_run_settings ([type]): [description]

        Returns:
            [type]: [description]
        """
        process_parameters = ProcessParameters(deepcopy(self._settings), seed=self._generate_seed())

        return exec(self._settings.simulation_core.main_function)(
            self._settings.simulation_core.arguments,
            individual_run_settings
        )

    
    @staticmethod
    def _generate_seed():
        return random.random()

    def _generate_samples(self, ) -> np.array:
        # sampleset
        sampleset = [
            self._transform_sample(sample_set=sample)
            for sample in 
                saltelli.sample(
                    self._problem,
                    self._settings.sensitivity_analysis.num_runs,
                    calc_second_order=False,
                )
        ]

        return np.asarray(sampleset)
 
    def _transform_sample(self, sample_set: np.array):
        for i, sample in enumerate(sample_set):
            sample_set[i] = [variable_obj.distribution.params.transform(sa) 
                for sa, variable_obj in zip(sample, self._settings.sensitivity_analysis.variables)
            ]
        return sample_set


    def _compose_problem(self, ) -> dict:
        return {
            'num_vars': self._settings.sensitivity_analysis.variable_num,
            'names': self._settings.sensitivity_analysis.names,
            'bounds': [var.distribution.params.bounds 
                for var in self._settings.sensitivity_analysis.variables
            ]
        } 

    def main(self, settings) -> dict:
        results = []
        for i in self._settings.sensitivity_analysis.num_runs:
            funcs = []
            for _ in range(self._settings.simulation_core.cpu_cores):
                # remote_sim = self._f.remote()
                
                funcs.append(remote_sim.run.remote())

            fs = [self._f.remote() for _ in range(self._settings.simulation_core.cpu_cores)]
            
            fs = [fs.run.remote() for f in fs]

    def _distributed_manager(self, ):
        

if __name__ == "__main_":





# if __name__ == "__main__":

#     ROOT