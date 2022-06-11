import glob
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Union

# external imports
import ray
from omegaconf import DictConfig
from SASUMO.utils.fleet_composition import (
    create_veh_distributions,
)

# internal imports
from SASUMO.params import ProcessConfig
from SASUMO.utils import beefy_import
from SASUMO.params.configuration import ReplayProcessConf
from SASUMO.utils.utils import create_folder
from SASUMO.utils.sumo_dist_builder import create_distribution
from SASUMO.utils.constants import TEMP_PATTERN, SUMO_HOME


class BaseSUMOFunc:
    def __init__(
        self,
        yaml_params: Union[dict, ReplayProcessConf],
        replay: bool = False,
        *args,
        **kwargs,
    ):

        # create the yaml params
        if isinstance(yaml_params, ReplayProcessConf):
            self._params = yaml_params
        else:
            self._params = ProcessConfig(**yaml_params)

        # log if replay mode or not
        self._replay = replay

        self._dump_parameters()

        self._output_handler = self._create_output_handler()

        # TODO: create a prototype of Simulation (similar to OpenAI Gym)
        self._simulation: object = None

        # print that I am starting
        print(f"{self._params.Metadata.run_id} is spawning")

    def _dump_parameters(
        self,
    ):
        if not self._replay:
            # create the directory
            create_folder(self._params.Metadata.cwd)
            # save the file
            self._params.to_yaml(os.path.join(self._params.Metadata.cwd, "params.yaml"))
            # create a logger
            self._params.create_logger()

    def _create_output_handler(
        self,
    ):
        mod = beefy_import(self._params.get("Output", {}).get("module"))
        return mod(
            cwd=self._params.Metadata.cwd,
            **self._params.get("Output", {}).arguments.kwargs,
        )

    def _create_simulation(self, **kwargs):
        mod = beefy_import(
            self._params.SimulationCore.SimulationFunction.module, internal=False
        )

        return mod(
            *self._params.SimulationCore.SimulationFunction.arguments.get("args", []),
            **self._params.SimulationCore.SimulationFunction.arguments.get(
                "kwargs", {}
            ),
            **kwargs,
        )

    @property
    def output(
        self,
    ) -> float:
        return self._output()

    def _output(
        self,
    ) -> float:
        pass

    def create_veh_distribution(
        self,
        *args: List[DictConfig],
        output_file_name: os.PathLike,
        distribution_size: int,
        distribution_name: str,
    ) -> None:
        """
        Creating the text input file
        """

        create_veh_distributions(
            args,
            output_file_name=output_file_name,
            distribution_size=distribution_size,
            distribution_name=distribution_name,
            seed=self._params.Metadata.random_seed,
        )

    def post_processing(
        self,
    ) -> None:
        # TODO: internal=False is not always true, maybe a usecase for retry
        mod = beefy_import(self._params.get("PostProcessing").module, internal=False)

        mod(
            *self._params.get("PostProcessing").arguments.get("args", ()),
            **self._params.get("PostProcessing").arguments.get("kwargs", {}),
        ).main()

    def cleanup(
        self,
    ) -> None:
        # delete files, but only if not replay mode
        if not self._replay:
            for f in glob.glob(
                os.path.join(self._params.Metadata.cwd, TEMP_PATTERN.join(["*"] * 2))
            ):
                os.remove(f)

    def run_simulation(self, *args, **kwargs) -> Any:
        return self._create_simulation(*args, **kwargs).main()


class EmissionsSUMOFunc(BaseSUMOFunc):
    def __init__(
        self,
        yaml_params: dict,
        replay: bool = False,
        replay_root: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(yaml_params, replay, replay_root, *args, **kwargs)

    @property
    def output(self):
        return self._output_handler.y

    def _handle_matlab(
        self,
    ):
        """
        This function should handle matlab.
        This means that it should connect to a running matlab instance and pass said connection to the main function running the simulation
        """
        pass

    def execute_generator_functions(
        self,
    ):
        output_dict = {}
        for gen in self._params.get("Generators", []):
            self._params.log_info(f"Running {gen.function}")
            f = getattr(self, gen.function)
            out = f(*gen.arguments.args or [], **gen.arguments.kwargs)
            if gen.get("passed_to_simulation", False):
                output_dict[gen.output_name] = out
        return output_dict

    def run(
        self,
    ):
        """
        This is the main function. It:
            1. creates a folder location from where to work from
            2. generates the input files for the varying parameters
            3. runs the specific runner. It should have a "main" method.
               I can create an abstract base class later
        """
        simulation_kwargs = self.execute_generator_functions()

        self._simulation = self._create_simulation(**simulation_kwargs)

        # run the simulation
        self._simulation.main()

        self.post_processing()

        y = self.output

        print(f"{self._params.Metadata.run_id} is finished. Cleaning up...")

        self.cleanup()

        return y


@ray.remote
class RemoteEmissionsSUMOFunc(EmissionsSUMOFunc):
    def __init__(
        self,
        yaml_params: dict,
        replay: bool = False,
        replay_root: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(yaml_params, replay, replay_root, *args, **kwargs)

    @ray.method(num_returns=1)
    def run(
        self,
    ):
        return super().run()
