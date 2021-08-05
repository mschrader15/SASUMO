import os
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


def _stringify_list(_l: list) -> str:
    ", ".join(map(_l, float))


@ray.remote
class BaseSUMOFunc:
    def __init__(self, params: Parameters, *args, **kwargs):
        self._params = deepcopy(params)
        self._folder = self.create_folder()

    def _dump_parameters(self, ):
        self._params.save(self._folder)

    def run(self, *args, **kwargs):
        # dump the parameters at run time
        self._dump_parameters()

        # then call the inner run function
        self._run(*args, **kwargs)

    def _run(self, ):
        pass

    def create_folder(self, ) -> str:
        folder = os.path.join(self._params['working_folder'], "-".join(
            [str(datetime.now()).replace(":", "-"), uuid.uuid4().hex]))
        os.makedirs(folder, exist_ok=True)
        return folder

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
    # def prior_veh_dist()


class EmissionsSUMOFunc(BaseSUMOFunc):

    def __init__(self, params, *args, **kwargs):

        from SASUMO.SASUMO.output import TotalEmissionsHandler

        super().__init__(params, *args, **kwargs)
        self._output_handler = TotalEmissionsHandler(params)

    def _output(self):
        return self._output_handler.y

    def run(self, ):
        """
        This is the main function. It: 
            1. creates a folder location from where to work from
            2. generates the input files for the varying parameters
            2. runs the specific runner
            3. 
        """

        return self.output
