import glob
import os
from pathlib import Path
import subprocess
from typing import Any, List, Union


import numpy as np
import ray

# internal imports
from SASUMO.params import ProcessSASUMOConf
from SASUMO.utils import FleetComposition, beefy_import
from SASUMO.params.configuration import ReplayProcessConf
from SASUMO.utils.utils import create_folder

TEMP_PATTERN = "__temp__"
SUMO_HOME = os.environ.get("SUMO_HOME")


class BaseSUMOFunc:
    def __init__(
        self,
        yaml_params: Union[dict, ReplayProcessConf],
        replay: bool = False,
        replay_root: str = None,
        *args,
        **kwargs,
    ):

        # create the yaml params
        if isinstance(yaml_params, ReplayProcessConf):
            self._params = yaml_params
        else:
            self._params = ProcessSASUMOConf(**yaml_params)

        # log if replay mode or not
        self._replay = replay

        self._dump_parameters()

        self._output_handler = self._create_output_handler()

        # TODO: create a prototype of Simulation (similar to OpenAI Gym)
        self._simulation: object = None

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
        mod = beefy_import(self._params.SensitivityAnalysis.Output.module)
        return mod(
            cwd=self._params.Metadata.cwd,
            **self._params.SensitivityAnalysis.Output.arguments.kwargs,
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
            replay=self._replay,
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
        *args: List[object],
        output_file_name,
        distribution_size,
        distribution_common,
        delta=None,
    ) -> None:
        """
        Creating the text input file
        """
        tmp_dist_input_file = os.path.join(
            self._params.Metadata.cwd, f"{TEMP_PATTERN}vehDist.txt"
        )

        for type_group in args:

            group_name = type_group[0].group

            text_parameters = distribution_common[group_name].distribution_parameters

            # compose the variables
            vary_lines = []
            for var in type_group:
                center = var.val
                width = var.distribution.params.width
                vary_lines.append(
                    f"{var.variable_name};uniform({center - width / 2},{center + width / 2});[{var.distribution.params.min},{var.distribution.params.max}]"
                )

            if delta:
                # add in the delta (if delta)
                center = var.val
                width = delta.distribution.params.width
                vary_lines.append(
                    f"{delta.variable_name};uniform({center - width / 2},{center + width / 2});[{var.distribution.params.min},{var.distribution.params.max}]"
                )

            text_parameters = "\n".join([text_parameters, *vary_lines])

            with open(tmp_dist_input_file, "w") as f:
                """
                Create a list of rows to write to the text file
                """
                f.write(text_parameters)

            subprocess.run(
                [
                    "python",
                    f"{SUMO_HOME}/tools/createVehTypeDistribution.py",
                    tmp_dist_input_file,
                    "--name",
                    distribution_common[group_name].distribution_name,
                    "-o",
                    output_file_name,
                    "--size",
                    str(distribution_size),
                ]
            )

        # os.remove(tmp_dist_input_file)

        return output_file_name

    def fleet_composition(
        self, base_route_file, fleet_composition, controlled_dist_name, other_dist_name
    ):
        """
        This function creates a route distribution based on some fleet composition

        """

        output_file_path = os.path.join(
            self._params.Metadata.cwd, TEMP_PATTERN + Path(base_route_file).name
        )

        fleet = {
            controlled_dist_name: fleet_composition.distribution.sa_value,
            other_dist_name: 1 - fleet_composition.distribution.sa_value,
        }

        f = FleetComposition(
            fleet, seed=self._params.Metadata.random_seed, route_file=base_route_file
        )

        f.replace_vehType(output_path=output_file_path)

        return output_file_path

    def post_processing(
        self,
    ) -> None:
        # TODO: internal=False is not always true, maybe a usecase for retry
        mod = beefy_import(
            self._params.SensitivityAnalysis.PostProcessing.module, internal=False
        )

        mod(
            *self._params.SensitivityAnalysis.PostProcessing.arguments.get("args", ()),
            **self._params.SensitivityAnalysis.PostProcessing.arguments.get(
                "kwargs", {}
            ),
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
        for gen in self._params.SensitivityAnalysis.Generators:
            self._params.log_info(f"Running {gen.function}")
            f = getattr(self, gen.function)
            out = f(*gen.arguments.args or [], **gen.arguments.kwargs)
            if gen.passed_to_simulation:
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
