import glob
import importlib
import os
from pathlib import Path
import subprocess
import sys
from typing import List
import uuid
from abc import ABCMeta
from copy import deepcopy
from datetime import datetime

import numpy as np
import ray
# internal imports
from params import ProcessParameters, Settings4SASUMO
from params import SensitivityAnalysisGroup
from utils import FleetComposition, beefy_import

from .output import TotalEmissionsHandler

# from sumolib.vehicle.vehtype_distribution import CreateVehTypeDistribution


# import subprocess
# from sumolib.vehicle import CreateMultiVehTypeDistributions

TEMP_PATTERN = "__temp__"


def _stringify_list(_l: list) -> str:
    ", ".join(map(_l, float))


class BaseSUMOFunc:

    def __init__(self,
                 yaml_params: Settings4SASUMO,
                 sample: np.array,
                 seed: int,
                 sample_num: int,
                 *args,
                 **kwargs):

        self._params = ProcessParameters(
            yaml_settings=yaml_params, sample=sample, seed=seed, sample_num=sample_num)
        # self._folder =
        # self._params.save()
        self._dump_parameters()

        # TODO: create a prototype of Simulation (similar to OpenAI Gym)
        self._simulation: object = None

    def _dump_parameters(self, ):
        self._params.save(
            os.path.join(self._params.WORKING_FOLDER, 'run_params.json')
        )

    # def run(self, *args, **kwargs):
    #     # dump the parameters at run time
    #     self._dump_parameters()

    #     # then call the inner run function
    #     return self._run(*args, **kwargs)

    # def _run(self, ):
    #     pass
    #     # return folder
    
    def _create_output_handler(self, ):
        mod = beefy_import(self._params._sensitivity_analysis.output.module)
        return mod(cwd=self._params.WORKING_FOLDER, **self._params._sensitivity_analysis.output.arguments)


    @property
    def output(self, ) -> float:
        return self._output()

    def _output(self, ) -> float:
        pass

    # def create_veh_defintion(self, ) -> None:
    #     """Call SUMO's https://github.com/eclipse/sumo/blob/master/tools/createVehTypeDistribution.py here"""
    #     # self._params.veh_dist_location = os.path.join(self._folder, self._params.VEH_DIST_NAME + ".in.xml")

    #     creator = CreateMultiVehTypeDistributions()

    #     for param in self._params.CAR_FOLLOWING_PARAMETERS.PARAMETERS:

    #         creator.register_veh_type_distribution(veh_type_dist=CreateVehTypeDistribution(**param), )

    #     creator.to_xml(file_path=self._params.VEH_DIST_SAVE_PATH)

    #     creator.save_myself(file_path=self._params.VEH_DIST_SAVE_PATH)

    def create_veh_distribution(self, output_file_name, distribution_size, args: List[SensitivityAnalysisGroup]) -> None:
        """
        Creating the text input file
        """
        tmp_dist_input_file = os.path.join(
            self._params.WORKING_FOLDER,  TEMP_PATTERN + "vehDist.txt"
        )

        veh_dist_file = os.path.join(
            self._params.WORKING_FOLDER,  TEMP_PATTERN + output_file_name
        )

        # veh_dist_file = self._params.set_var_inline(
        #     self._params.create_working_path(self._params.VEH_DIST_FILE)
        # )

        for group in args:

            text_parameters = group.generator_arguments

            # compose the variables
            vary_lines = []
            for var in group.variables:
                center = var.distribution.params.sa_value
                width = var.distribution.params.width
                vary_lines.append(
                    f"{var.name};uniform({str(center - width / 2)},{str(center + width / 2)})")

            text_parameters = "\n".join([text_parameters, *vary_lines])
            
            with open(tmp_dist_input_file, 'w') as f:
                """
                Create a list of rows to write to the text file
                """
                f.write(text_parameters)

            subprocess.run([f"{self._params.SUMO_HOME}/tools/createVehTypeDistribution.py",
                            tmp_dist_input_file,
                            '--name', group.name,
                            '-o', veh_dist_file,
                            '--size', distribution_size])

        os.remove(tmp_dist_input_file)

    def fleet_composition(self, base_route_file, fleet_composition):
        """
        This function 
        """

        output_file_path = os.path.join(self._params.WORKING_FOLDER,
                                        TEMP_PATTERN + Path(base_route_file).name)

        f = FleetComposition(fleet_composition,
                             seed=self._params.SEED,
                             route_file=base_route_file)

        f.replace_vehType(
            output_path=output_file_path
        )

        return output_file_path

    def cleanup(self, ) -> None:
        # delete files
        for f in glob.glob(os.path.join(self._params.WORKING_FOLDER, TEMP_PATTERN.join(['*'] * 2))):
            os.remove(f)


# @ray.remote


class EmissionsSUMOFunc(BaseSUMOFunc):

    def __init__(self, yaml_settings, sample, seed, *args, **kwargs):

        super().__init__(yaml_settings, sample, seed, *args, **kwargs)

        self._output_handler = TotalEmissionsHandler(self._params)
        self._simulation = beefy_import(self._params.simulation)
        # self._simulation = importlib.import_module(self._params.)

    @property
    def output(self):
        return self._output_handler.y

    def _handle_matlab(self, ):
        """
        This function should handle matlab. 
        This means that it should connect to a running matlab instance and pass said connection to the main function running the simulation 
        """
        pass

    def execute_generator_functions(self, ):
        output_dict = {}
        for var in self._params.sensitivity_analysis.variables:
            self._params.log_info(f"Running {var.generator.function}")
            f = getattr(self, var.generator.function)
            out = f(**var.generator.arguments)
            if var.generator.passed_to_simulation:
                output_dict[var.generator.name]
        return output_dict

    # @ray.method(num_returns=1)
    def run(self, ):
        """
        This is the main function. It: 
            1. creates a folder location from where to work from
            2. generates the input files for the varying parameters
            2. runs the specific runner. It should have a "main" method. 
               I can create an abstract base class later
        """

        simulation_kwargs = self.execute_generator_functions()

        # self.create_veh_distribution()
        # # self.implement_fleet_composition()
        # self._handle_matlab()

        # TODO: turn this into a function and pass the correct parameters given YAML settings
        self._simulation = self._simulation(**simulation_kwargs)

        # run the simulation
        self._simulation.main()

        return self.output
