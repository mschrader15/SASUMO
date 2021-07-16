from copy import deepcopy
from typing import Any, Hashable, Union
import json


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


class CarFollowingParameters:
    
    def __init__(self, parameter_dict):
        
        self.MODEL: str = _remover(parameter_dict, 'name') if parameter_dict else None
        self.PARAMETERS: dict = _remover(parameter_dict, 'model-parameters') if parameter_dict else None


class Parameters(_FlexibleDict):

    def __init__(self, parameter_json) -> None:

        params = self._load_json(parameter_json)
        self.CAR_FOLLOWING_PARAMETERS = CarFollowingParameters(_remover(params, 'car-following-parameters'))
        
        """ Vehicle Distribution Parameters"""
        self.VEH_DIST_NAME = _remover(params, 'veh_dist')
        self.veh_dist_location: str = None

    @staticmethod
    def _load_json(input_object: Union[str, dict]) -> dict:
        if isinstance(input_object, dict):
            return input_object
        with open(input_object, "rb") as f:
            return json.load(f)


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

    
