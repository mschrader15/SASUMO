from copy import deepcopy
import os
import json
import sys
import click

# from ..creator import SASUMO
from SASUMO.params import Settings4SASUMO
# from ..functions import 
from SASUMO.utils import path_constructor, beefy_import


class ReplaySASUMO:

    def __init__(self, replay_root: str, sample_num: int, new_folder_location: str = None) -> None:
        # super().__init__(yaml_file_path)
        self._replay_root = replay_root
        
        self._s = Settings4SASUMO(os.path.join(replay_root, "settings.yaml"))
        
        # update the path
        self._update_path()
        
        self._s_num = sample_num
        self._s_folder = os.path.join(replay_root, f"sample_{self._s_num}",) 
        self._s_output_folder = os.path.join(self._s_folder, new_folder_location or "replay")

        #TODO: This is hacky. Should really update the path to file when the YAML is saved. 
        # If someone else ends up using this project, then they can fix lol
        self._s.simulation_core.simulation_function.arguments.kwargs['settings'] = os.path.join(self._s_folder, 'simulation_params.json') 
        
        # make the replay folder
        self._make_replay_folder()
        
        self._sample = self._get_sample_values()
        self._fn = self._get_fn()


    def _make_replay_folder(self, ):
        try:
            os.makedirs(self._s_output_folder, )
        except FileExistsError:
            print(f"{self._s_output_folder} already exists. Continuing on dangerously")
    
    def _get_sample_values(self, ):
        with open(os.path.join(self._s_folder, "sa_values.json"), 'r') as f:
            return json.load(f)

    def _get_fn(self, ):
        return beefy_import(
            self._s.simulation_core.manager_function.module.replace("Remote", "")
        )

    def main(self, ):
        self._fn(
            yaml_settings=deepcopy(self._s),
            sample=self._sample,
            seed=None,
            sample_num=int(self._s_num),
            replay=True,
            replay_root=self._s_output_folder
        ).run()

    def _update_path(self, ):
        for new_path in [self._s.simulation_core.manager_function.path, self._s.simulation_core.simulation_function.path]:
            if new_path:
                if "${" in new_path:
                    new_path = path_constructor(new_path)
                sys.path.append(new_path)
    

@click.command()
@click.option('--results_dir', help="The location to same the replay outputs too")
@click.option('--sample_num', help="The sample number that you wish to replay")
@click.argument('experiment_directory')
def run(results_dir, sample_num, experiment_directory):
    replayer = ReplaySASUMO(experiment_directory, sample_num, results_dir)
    replayer.main()


if __name__ == "__main__":

    run()
