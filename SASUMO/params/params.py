from datetime import datetime
import sys
import os
# from copy import deepcopy
from typing import Any, Dict, Hashable, List, Union
import json
import uuid
import yaml
# import pendulum
# from dataclasses import dataclass
import logging
from utils import path_constructor
from .yaml_handler import Settings4SASUMO

""" Call this once to error out before SUMO runs"""
# MAKING SURE THAT SUMO_HOME IS IN THE PATH
if "SUMO_HOME" in os.environ:
    SUMO_HOME = os.path.join(os.environ["SUMO_HOME"])
    sys.path.append(SUMO_HOME)
else:
    sys.exit("please declare environmental variable 'SUMO_HOME'")


def _remover(d: dict, p: Hashable, default=None) -> Any:
    try:
        return d.pop(p)
    except KeyError:
        return default


def create_folder(folder_root: str, unique_id: str = None) -> str:
    folder = os.path.join(
        folder_root, uuid.uuid4().hex if not unique_id else unique_id)
    os.makedirs(folder, exist_ok=True)
    return folder


class _FlexibleDict:
    
    def __init__(
        self,
    ) -> None:

        super(_FlexibleDict, self).__init__()

    def compose(self, _dict: dict) -> object:
        for key, value in _dict.items():
            self[key.upper()] = (
                _FlexibleDict().compose(value) if isinstance(value, dict) else value
            )
        return self

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getattribute__(self, name: str) -> Any:
        """
        This is some funkiness to protect calls to missing attributes
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None

    def __getitem__(
        self,
        name: str,
    ) -> Any:
        return getattr(self, name.upper(), None)

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value

    def items(self, ):
        return self.__dict__.items()

    def save(self, location: str):
        """
        Save this beast of a class to a json file

        Args:
            location (str): where to save the file too
        """
        with open(location, "w") as f:
            f.write(
                json.dumps(
                    {val: self[val]
                        for val in dir(self) if "__" not in val[:2]},
                    default=lambda o: o.__dict__,
                    sort_keys=True,
                    indent=4,
                )
            )


# class _VehAttributes:

#     def __init__(self, parameter_dict):

#         self.NAME: str = _remover(parameter_dict, 'name')
#         self.PARAMETERS: dict = _remover(parameter_dict, 'model-parameters')
#         self.SIZE: int = _remover(parameter_dict, 'size', default=100)
#         self.DECIMAL_PLACES: int = _remover(parameter_dict, 'size', default=3)
#         self.SEED: int = _remover(parameter_dict, 'size', default=3)
#         self._comp: float = 0

#     @property
#     def composition(self, ):
#         return self._comp

#     @composition.setter
#     def composition(self, arg):
#         self._comp = arg


# class 

# class _VehDist:

#     def __init__(self, parameters: dict) -> None:

#         self.VEH_DISTS: Dict[str, _VehAttributes] = {
#             key: _VehAttributes(value) for key, value in parameters.items()}

#         """ Handling the Fleet Composition """
#         for distr_name, percent in parameters['fleet-composition']:
#             self.VEH_DISTS[distr_name].composition = percent

#     @property
#     def composition(self, ) -> Dict[str, float]:
#         return {veh_attr.NAME: veh_attr.composition for _, veh_attr in self.VEH_DISTS.items()}


class ReplayParameters(_FlexibleDict):

    """
    ProcessParameters is the "organizational class" for an individual simulation process

    The "parameter_json" passed to this class should include the simulation specifics

    It allows for logging and will save itself and the parameters inside of it to the "working folder"
    """

    def __init__(self, parameter_json: Union[str, dict], seed: int, working_folder: str = None, replay_folder: str = None) -> None:
        """ Handle creating the logger and the folder location """

        self.WORKING_FOLDER = create_folder(
            working_folder) if working_folder else replay_folder

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self._create_log()

        """ Store the location of SUMO """
        self.SUMO_HOME = SUMO_HOME
        self.SEED = seed   
        params = self._load_json(parameter_json)

        """ Vehicle Distribution Parameters"""
        self.VEH_DIST = _VehDist(_remover(params, 'car-following-parameters'))

        """ Pass the rest of the parameters to myself. This isn't friendly for linter, 
        but is ultimately friendly for saving state
        """
        self.compose(params)

    def _create_log(self, ) -> None:
        fh = logging.FileHandler(os.path.join(
            self.WORKING_FOLDER, 'simulation.log'))
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def create_working_path(self, path: str, ) -> os.PathLike:
        return os.path.join(self.WORKING_FOLDER, os.path.split(path)[-1])

    def set_var_inline(self, var: Any, value: Any):
        self[var] = value
        try:
            self.log_info(f"Setting variable: {var} to {value}")
        except TypeError:
            self.log_info(
                f"Setting variable: {var} to value that can't be converted to string")
        return value

    def log_info(self, message) -> None:
        self.logger.info(message)

    @staticmethod
    def _load(input_object: Union[str, dict]) -> dict:
        if isinstance(input_object, dict):
            return input_object
        with open(input_object, "rb") as f:
            return json.load(f) if 'json' in os.path.splitext(input_object)[1] else yaml.load(f)


class ProcessParameters(_FlexibleDict, Settings4SASUMO):

    """
    ProcessParameters is the "organizational class" for an individual simulation process

    It is passed the global Sensitivity Analysis Setting

    It allows for logging and will save itself and the parameters inside of it to the "working folder"
    """

    def __init__(self, yaml_settings: Settings4SASUMO, seed: int, sample: list, sample_num: int = None) -> None:
        """ Handle creating the logger and the folder location """

        vars(self).update(vars(yaml_settings))



        self.WORKING_FOLDER = create_folder(
            self.sensitivity_analysis.working_root, unique_id=f"sample_{sample_num}" or None
        )


        """ Create the Logger"""
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self._create_log()

        """ Store the location of SUMO """
        self.SUMO_HOME = SUMO_HOME
        self.SEED = seed
        
        # params = self._load_json(parameter_json)

        """ Process the Sample """
        self.disperse_sample(sample)

        """ Vehicle Distribution Parameters"""
        # self.VEH_DIST = _VehDist(_remover(params, 'car-following-parameters'))

        """ Pass the rest of the parameters to myself. This isn't friendly for linter, 
        but is ultimately friendly for saving state
        """

        # self.compose(yaml_settings)

    # def _load_settings():

    def _create_log(self, ) -> None:
        fh = logging.FileHandler(os.path.join(
            self.WORKING_FOLDER, 'simulation.log'))
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    # def create_working_path(self, path: str, ) -> os.PathLike:
    #     return os.path.join(self.WORKING_FOLDER, os.path.split(path)[-1])

    # def set_var_inline(self, var: Any, value: Any):
    #     self[var] = value
    #     try:
    #         self.log_info(f"Setting variable: {var} to {value}")
    #     except TypeError:
    #         self.log_info(
    #             f"Setting variable: {var} to value that can't be converted to string")
    #     return value

    def log_info(self, message) -> None:
        self.logger.info(message)

    def disperse_sample(self, sample) -> None:
        for _s, distribution in zip(sample, self.sensitivity_analysis.variables):
            distribution.transform(_s)
        
    
    def save_settings(self, ):

        return self.save(
                os.path.join(self.WORKING_FOLDER, 'settings.json')
            )

        # [
        #     self.sensitivity_analysis.variables[
        #         i
        #     ].distribution.params.transform(sample)
        #     for i, sample in enumerate(sample_set)
        # ]


    # def transform_sample(self, sa_sumo: Settings4SASUMO, sample_set: dict) -> None:
    #     return [
    #         sa_sumo.sensitivity_analysis.variables[
    #             i
    #         ].distribution.params.transform(sample)
    #         for i, sample in enumerate(sample_set)
    #     ]

    # @staticmethod
    # def _load(input_object: Union[str, dict]) -> dict:
    #     if isinstance(input_object, dict):
    #         return input_object
    #     with open(input_object, "rb") as f:
    #         return json.load(f) if 'json' in os.path.splitext(input_object)[1] else yaml.load(f)


# if __name__ == "__main__":

#     ProcessParameters(yaml_settings=)
