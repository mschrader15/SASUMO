import ray
from copy import deepcopy
import subprocess

@ray.remote
class BaseSUMOFunc:
    def __init__(self, params, *args, **kwargs):
        self._params = deepcopy(params)

    def run(self, ):
        pass
    
    @property
    def output(self, ) -> float:
        return self._output()

    def _output(self, ) -> float:
        pass

    def create_veh_defintion(self, ) -> None:
        """Call SUMO's https://github.com/eclipse/sumo/blob/master/tools/createVehTypeDistribution.py here"""
        pass

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