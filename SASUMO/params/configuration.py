from copy import deepcopy
from dataclasses import dataclass
from typing import Any, List, Tuple

from datetime import datetime


from omegaconf import OmegaConf


class ProcessSASUMOConf:
    def __init__(
        self,
        base_conf: object,
        process_var: List,
        process_id: str,
        missing_dotlist: List[str],
    ) -> None:

        # set the base configuration
        self._base_conf = base_conf

        # save the process id
        self._base_conf.Metadata.run_id = process_id

        self.update_values(process_var)

        self._missing_dotlist = missing_dotlist

    def update_values(self, process_var: List) -> None:

        for var, process_var in zip(
            self._base_conf.SensitivityAnalysis.Variables.values(), process_var
        ):
            var.val = float(process_var)

    def to_yaml(self, file_path) -> None:
        self._base_conf.masked_copy(self._missing_dotlist)


class SASUMOConf:
    def __init__(
        self,
        file_path: str,
    ) -> None:

        OmegaConf.register_new_resolver(
            "datetime", lambda _: datetime.now().isoformat(), use_cache=True
        )

        OmegaConf.register_new_resolver(
            "group", lambda group: self._get_group(group), use_cache=True
        )

        self._s = OmegaConf.load(file_path)

        # set the missing keys
        self._set_missing_keys()

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._s[__name]
        except KeyError:
            return self.__getattribute__(__name)

    def _get_group(self, group: str):
        # This is probably not generalizable enough
        # TODO make this traverse the whole tree
        return [
            g
            for _, g in self.SensitivityAnalysis.variables.items()
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

        # create a sample conf object to save for each run
        self._missing_dotlist = [".".join(_key_list) for _key_list in missing_key_list]

    def generate_process(self, process_var: List, process_id: str) -> ProcessSASUMOConf:

        return ProcessSASUMOConf(
            OmegaConf.structured(self._s),
            process_var=process_var,
            process_id=process_id,
            missing_dotlist=self._missing_dotlist,
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
