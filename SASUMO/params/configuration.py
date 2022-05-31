from copy import deepcopy
import os
from random import sample
import re
from typing import Any, Dict, List
import logging

from datetime import datetime


from omegaconf import OmegaConf


OmegaConf.register_new_resolver(
    "datetime",
    lambda _: datetime.now().strftime("%m.%d.%Y_%H.%M.%S"),
    use_cache=True,
)

OmegaConf.register_new_resolver(
    "group",
    lambda x, *, _root_: SASUMOConf.get_group(
        x,
        _root_,
    ),
)


class ReplayProcessConf:
    def __init__(
        self,
        yaml_params: object,
        run_id: str,
        new_dir: str = "replay",
        sample_yaml_name: str = "params.yaml",
    ) -> None:

        # write the run id
        yaml_params.Metadata.run_id = run_id

        self._base_conf = OmegaConf.merge(
            yaml_params.to_omega(),
            OmegaConf.load(os.path.join(yaml_params.Metadata.cwd, sample_yaml_name)),
        )

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._base_conf[__name]
        except KeyError:
            return self.__getattribute__(__name)

    def update_simulation_output(self, path: str) -> None:
        self._base_conf.SimulationCore.output_path = path


class ProcessSASUMOConf:
    def __init__(
        self,
        yaml_params: object,
        process_var: List,
        process_id: str,
        missing_dotlist: List[str],
        random_seed: int,
    ) -> None:

        # set the base configuration
        self._base_conf = yaml_params

        # save the process id
        self._base_conf.Metadata.run_id = process_id

        # only write the random_seed if it has been set
        if random_seed:
            self._base_conf.Metadata.random_seed = random_seed

        self.update_values(process_var)

        # resolve the configuration, to save comp time later. Nothing will change from here on out
        self._missing_dotlist = missing_dotlist

        # create a logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        # self._create_log()

    def to_omega(
        self,
    ):
        return self._base_conf

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._base_conf[__name]
        except KeyError:
            return self.__getattribute__(__name)

    def create_logger(
        self,
    ) -> None:
        fh = logging.FileHandler(
            os.path.join(self._base_conf.Metadata.cwd, "simulation.log")
        )
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def update_values(self, process_var: List) -> None:

        for var, p_var in zip(
            self._base_conf.SensitivityAnalysis.Variables.values(), process_var
        ):
            # default is float
            mode = var.distribution.get("data_type", "float")
            var.val = eval(f"{mode}(p_var)")
            if var.distribution.get("data_transform", ""):
                var.val = eval(
                    var.distribution.data_transform.replace("val", "var.val")
                )

    def to_yaml(self, file_path: str) -> None:
        new_conf = [
            "=".join((dot_list, str(OmegaConf.select(self._base_conf, dot_list))))
            for dot_list in self._missing_dotlist
        ]
        # s = OmegaConf.masked_copy(self._base_conf, self._missing_dotlist)
        with open(file_path, "w") as f:
            OmegaConf.save(config=OmegaConf.from_dotlist(new_conf), f=f, resolve=False)


class SASUMOConf:
    def __init__(
        self,
        file_path: str,
        replace_root: bool = False
    ) -> None:

        self._s = OmegaConf.load(file_path)

        if replace_root:
            # this replaces the existing root with one relative to the files director
            self._s.Metadata.output = os.path.split(file_path)[:-1][0] 

        # set the missing keys
        self._set_missing_keys()

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._s[__name]
        except KeyError:
            return self.__getattribute__(__name)

    @staticmethod
    def get_group(group: str, root: object):
        # This is probably not generalizable enough
        # TODO make this traverse the whole tree
        # TODO: resolve
        return [
            g
            for _, g in root.SensitivityAnalysis.Variables.items()
            if g.get("group", False) == group
        ]

    def to_omega(
        self,
    ):
        return self._s

    def to_yaml(self, file_path: str, resolve: bool = True):
        if resolve:
            self._s.Metadata.output = str(self._s.Metadata.output)

        with open(file_path, "w") as f:
            OmegaConf.save(config=self._s, f=f, resolve=False)

    # def merge_run_test(self, run_settings: str, test_settings: str):
    def _recursive_missing_finder(
        self, node: OmegaConf, key_list: List[str], missing_key_list: List[List[str]]
    ):
        if isinstance(node, dict):
            iterator = node.items()
            for key, value in iterator:
                # OmegaConf missing value format
                if isinstance(value, str) and value == "???":
                    missing_key_list.append(key_list + [key])
                else:
                    self._recursive_missing_finder(
                        value, key_list + [key], missing_key_list
                    )

    def _set_missing_keys(
        self,
    ):

        # find the missing values in the initial configuration
        missing_key_list = []
        for key, value in OmegaConf.to_container(
            self._s, throw_on_missing=False
        ).items():
            key_list = [key]
            self._recursive_missing_finder(value, key_list, missing_key_list)

        # update the missing dotlist
        self._missing_dotlist = [".".join(_key_list) for _key_list in missing_key_list]

    def generate_process(
        self, process_var: List, process_id: str, random_seed: int
    ) -> Dict:

        # this must be pickleable
        return dict(
            yaml_params=deepcopy(OmegaConf.structured(self._s)),
            process_var=process_var,
            process_id=process_id,
            missing_dotlist=deepcopy(self._missing_dotlist),
            random_seed=random_seed,
        )
        # )


if __name__ == "__main__":

    settings = SASUMOConf(
        "/home/max/Development/airport-harper-sumo/SASUMO/input_files/car_following_params.yaml",
        5,
    )

    settings.get_sample_yaml()

    settings.create_run_config(5)

    settings.to_yaml(
        "/home/max/Development/airport-harper-sumo/SASUMO/input_files/car_following_params_test.yaml"
    )
