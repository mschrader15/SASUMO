from copy import deepcopy
import glob
import os
import shutil
import json5 as json
import sys
import click

# from ..creator import SASUMO
from SASUMO.params import Config, ReplayProcessConf
from SASUMO.functions.function import BaseSUMOFunc

# from ..functions import
from SASUMO.utils import beefy_import


class ReplaySASUMO:
    def __init__(
        self,
        replay_root: str,
        sample_num: int,
        new_folder_location: str = None,
        just_sim: bool = False,
    ) -> None:

        self._replay_root = replay_root
        self._just_sim = just_sim

        self._s = ReplayProcessConf(
            yaml_params=Config(os.path.join(replay_root, "sasumo_params.yaml")),
            run_id=sample_num,
            new_dir=new_folder_location,
        )

        # update the path
        self._update_path()
        
        # overwrite the simulation parameter file. This is very specific for my application unfortunately
        self._s.SimulationCore.SimulationFunction.arguments.kwargs.settings = \
            os.path.join(self._s.Metadata.cwd, "simulation_params.json")
        
        # update the simulation output path
        self._s.update_simulation_output(new_folder_location)

        # make the replay folder
        self._make_replay_folder()

        # copy over the existing sumo files. This is depended on ".xml" pattern match
        self._cp_sumo_files()

        # update the root output location
        self._s.Metadata.cwd = self._s.SimulationCore.output_path

        self._fn: BaseSUMOFunc = self._get_fn()


    def _update_path(
        self,
    ):

        for new_path in [
            self._s.SimulationCore.get("ManagerFunction", {}).get("path", ""),
            self._s.SimulationCore.SimulationFunction.get("path", ""),
        ]:
            if new_path:
                sys.path.append(new_path)

    def _make_replay_folder(
        self,
    ):
        try:
            os.makedirs(
                self._s.SimulationCore.output_path,
            )
        except FileExistsError:
            print(
                f"{self._s.SimulationCore.output_path} already exists. Continuing on dangerously"
            )

    def _get_fn(
        self,
    ) -> BaseSUMOFunc:
        return beefy_import(
            self._s.get("ManagerFunction").module.replace("Remote", "")
        )

    def _cp_sumo_files(
        self, 
    ) -> None:
        # this is too specific and too generic at the same time. 
        # TODO: Fix this
        for f in glob.glob(
                os.path.join(self._s.Metadata.cwd, "*.xml")
            ):
                shutil.copy(
                    f,
                    self._s.SimulationCore.output_path
                )

    def main(
        self,
    ):
        mod = self._fn(
            yaml_params=self._s,
            replay=True,
        )

        if self._just_sim:
            mod.run_simulation()
        else:
            mod.main()


@click.command()
@click.option("--results-dir", help="The location to same the replay outputs too")
@click.option("--sample-num", help="The sample number that you wish to replay")
@click.option("--just-sim", is_flag=True, help="Run just the simulation. Don't regenerate input files")
@click.argument("experiment_directory")
def run(results_dir, sample_num, just_sim, experiment_directory):
    replayer = ReplaySASUMO(experiment_directory, sample_num, results_dir, just_sim)
    replayer.main()


if __name__ == "__main__":

    run()
