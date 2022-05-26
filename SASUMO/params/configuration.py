from copy import deepcopy
import os
from typing import Any, List
import logging

from datetime import datetime


from omegaconf import OmegaConf


# elevating this to the module level
OmegaConf.register_new_resolver(
    "datetime", lambda _: datetime.now().strftime("%m.%d.%Y_%H.%M.%S"), use_cache=True
)

OmegaConf.register_new_resolver(
    "group", lambda x, *,  _root_: SASUMOConf._get_group(x,  _root_, )
)



class ProcessSASUMOConf:
    def __init__(
        self,
        base_conf: object,
        process_var: List,
        process_id: str,
        missing_dotlist: List[str],
        random_seed: int,
    ) -> None:

        # set the base configuration
        self._base_conf = base_conf

        # 
        # self._base_conf.register

        # save the process id
        self._base_conf.Metadata.run_id = process_id
        self._base_conf.Metadata.random_seed = random_seed
        self.update_values(process_var)
        
        # resolve the configuration, to save comp time later. Nothing will change from here on out
        self._missing_dotlist = missing_dotlist

        # create a logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        # self._create_log()

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

        for var, process_var in zip(
            self._base_conf.SensitivityAnalysis.Variables.values(), process_var
        ):
            var.val = float(process_var)

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
    ) -> None:

        self._s = OmegaConf.load(file_path)

        # set the missing keys
        self._set_missing_keys()

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._s[__name]
        except KeyError:
            return self.__getattribute__(__name)

    @staticmethod
    def _get_group(group: str, root: object):
        # This is probably not generalizable enough
        # TODO make this traverse the whole tree
        # TODO: resolve
        return [
            g
            for _, g in root.SensitivityAnalysis.Variables.items()
            if g.get("group", False) == group
        ]

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
    ) -> ProcessSASUMOConf:

        return ProcessSASUMOConf(
            deepcopy(OmegaConf.structured(self._s)),
            process_var=process_var,
            process_id=process_id,
            missing_dotlist=self._missing_dotlist,
            random_seed=random_seed,
        )


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
