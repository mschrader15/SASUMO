import os
from copy import deepcopy
from typing import Any, Dict, Hashable, Union
import json
import yaml
from dataclasses import dataclass


def _remover(d: dict, p: Hashable, default=None) -> Any:
    try:
        return d.pop(p)
    except KeyError:
        return default


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


# class _Sampleable:

#         def __init__(self, max: Any, min: Any) -> None:
#             self.max = max
#             self.min = min
            
#         def 


class _VehAttributes:
    
    def __init__(self, parameter_dict):

        self.NAME: str = _remover(parameter_dict, 'name')
        self.PARAMETERS: dict = _remover(parameter_dict, 'model-parameters') 
        self.SIZE: int = _remover(parameter_dict, 'size', default=100)
        self.DECIMAL_PLACES: int = _remover(parameter_dict, 'size', default=3)
        self.SEED: int = _remover(parameter_dict, 'size', default=3)


class _VehDist:

    def __init__(self, parameters: dict) -> None:

        
        self.PARAMETERS: Dict[str: _VehAttributes] = {key: _VehAttributes(value) for key, value in parameters.items()}

        """ Handling the Fleet Composition """
        max_count = max([(name, veh_attr.SIZE) for name, veh_attr in self.PARAMETERS.items()], key=lambda item:item[1])
        lower_num = int(max_count[0] * (1 / 100) * parameters['fleet_composition'])
        
        max_count = lower_num * 
        


class Parameters(_FlexibleDict):

    def __init__(self, parameter_json) -> None:

        """ Store the location of SUMO """
        self.SUMO_HOME = os.environ('SUMO_HOME')
        
        self.SEED = 22   # TODO: figure out where the random seed is set 

        params = self._load_json(parameter_json)

        self.VEH_DIST = _VehDist(_remover(params, 'car-following-parameters'))
        
        """ Vehicle Distribution Parameters"""
        self.VEH_DIST_NAME = _remover(params, 'veh_dist')
        self.veh_dist_location: str = None

    @staticmethod
    def _load(input_object: Union[str, dict]) -> dict:
        if isinstance(input_object, dict):
            return input_object
        with open(input_object, "rb") as f:
            return json.load(f) if 'json' in os.path.splitext(input_object)[1] else yaml.load(f)



    def save(self, location: str):
        """
        Save this beast of a class to a json file

        Args:
            location (str): where to save the file too
        """
        with open(location, "w") as f:
            f.write(
                json.dumps(
                    {val: self[val] for val in dir(self) if "__" not in val[:2]},
                    default=lambda o: o.__dict__ if not isinstance(o, pendulum.DateTime) else str(o),
                    sort_keys=True,
                    indent=4,
                )
            )

    
