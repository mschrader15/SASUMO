import os
import sys

from sumolib.vehicle.vehtype_distribution import CreateVehTypeDistribution
import ray
import uuid
# import subprocess
from sumolib.vehicle import CreateMultiVehTypeDistributions 
from abc import ABCMeta
from copy import deepcopy
from datetime import datetime
from .params import Parameters

""" Call this once to error out before SUMO runs"""
# MAKING SURE THAT SUMO_HOME IS IN THE PATH
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("please declare environmental variable 'SUMO_HOME'")


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

    def create_veh_defintion(self, ) -> None:
        """Call SUMO's https://github.com/eclipse/sumo/blob/master/tools/createVehTypeDistribution.py here"""
        # self._params.veh_dist_location = os.path.join(self._folder, self._params.VEH_DIST_NAME + ".in.xml")

        creator = CreateMultiVehTypeDistributions()

        for param in self._params.CAR_FOLLOWING_PARAMETERS.PARAMETERS:

            creator.register_veh_type_distribution(veh_type_dist=CreateVehTypeDistribution(**param), )

        creator.to_xml(file_path=self._params.VEH_DIST_SAVE_PATH)
        
        creator.save_myself(file_path=self._params.VEH_DIST_SAVE_PATH)




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
            2. 
            3. 
        """

        return self.output
