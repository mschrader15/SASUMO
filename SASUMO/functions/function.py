import os
import glob
import subprocess
import sys
# from sumolib.vehicle.vehtype_distribution import CreateVehTypeDistribution

import ray
import uuid

# import subprocess
# from sumolib.vehicle import CreateMultiVehTypeDistributions

from abc import ABCMeta
from copy import deepcopy
from datetime import datetime
from ..params import Parameters
from ..utils import FleetComposition
from .output import TotalEmissionsHandler


def _stringify_list(_l: list) -> str:
    ", ".join(map(_l, float))


@ray.remote
class BaseSUMOFunc:
    def __init__(self, params: Parameters, *args, **kwargs):

        self._params = deepcopy(params)
        # self._folder = 

    def _dump_parameters(self, ):
        self._params.save(self._folder)

    @ray.method(num_returns=1)
    def run(self, *args, **kwargs):
        # dump the parameters at run time
        self._dump_parameters()

        # then call the inner run function
        return self._run(*args, **kwargs)

    def _run(self, ):
        pass
        # return folder

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

    def create_veh_distribution(self, ) -> None:
        """
        Creating the text input file
        """

        tmp_dist_input_file = os.path.join(
            self._params.WORKING_FOLDER,  "_vehDist_temp.txt")

        veh_dist_file = self._params.set_var_inline(
            self._params.create_working_path(self._params.VEH_DIST_FILE)
            )

        for _, vehType in self._params.VEH_DIST.PARAMETERS.items():

            with open(tmp_dist_input_file, 'w') as f:
                """
                Create a list of rows to write to the text file
                """
                for paramter, value in vehType:
                    f.write(
                        '; '.join([paramter, ] + value if isinstance(value, list) else [value]))

            subprocess.run([f"{self._params.SUMO_HOME}/tools/createVehTypeDistribution.py", 
                            tmp_dist_input_file,
                            '--name', vehType.NAME, 
                            '-o', veh_dist_file,
                            '--size', vehType.SIZE])

        os.remove(tmp_dist_input_file)

    def implement_fleet_composition(self, ):
        """
        This function 
        """

        f = FleetComposition(self._params.VEH_DIST.composition,
                             seed=self._params.SEED, route_file=self._params.ROUTE_FILE)

        f.replace_vehType(
            output_path=self._params.set_var_inline(
                self._params.create_working_path(self._params.ROUTE_FILE)
            )
        )

    def cleanup(self, ) -> None:
        for f in glob.glob(f"{self._params.WORKING_FOLDER}/*.temp.*", ):
            os.remove(f)

        self._dump_parameters()    

    # def prior_veh_dist()


class EmissionsSUMOFunc(BaseSUMOFunc):

    def __init__(self, params, *args, **kwargs):

        exec()

        super().__init__(params, *args, **kwargs)
        self._output_handler = TotalEmissionsHandler(params)

    @property
    def output(self):
        return self._output_handler.y

    def _handle_matlab(self, ):
        """
        This function should handle matlab. 
        This means that it should connect to a running matlab instance and pass said connection to the main function running the simulation 
        """
        pass

    def run(self, ):
        """
        This is the main function. It: 
            1. creates a folder location from where to work from
            2. generates the input files for the varying parameters
            2. runs the specific runner
            3. 
        """
        self.create_folder()

        self.create_veh_distribution()
        self.implement_fleet_composition()

        self._handle_matlab()

        

        return self.output
