import os
import shutil
from dataclasses import dataclass
from typing import Any, Generator, List, Tuple, Union

import yaml

# from utils import path_constructor


# class PathHandler:

#     def __init__(self, base_path: str) -> None:

#         self._cwd = base_path
    
#     def _

#     def handle_path(self, arg: Any) -> Any:
#         if isinstance(arg, str):
#             return path_constructor(arg, self._cwd)
#         return arg

#     def update_cwd(self, base_path: str) -> None:
#         self._cwd = base_path


@dataclass
class _Dist:

    def transform(self, value: float) -> Any:
        self.sa_value = self._transform(value)


    def _transform(self, value: float) -> Any:
        return value

    @property
    def sa_value(self, ) -> Any:
        return self._sa_value

    @sa_value.setter
    def sa_value(self, val: Any) -> None:
        self._sa_value = val


@dataclass
class _UniformDist(_Dist):

    min: float
    max: float
    width: float = None

    def _transform(self, value: float) -> Any:
        return value

    @property
    def bounds(self, ) -> Tuple[float]:
        return self.min, self.max


@dataclass
class _UniformSample(_Dist):
    categorical: list

    @property
    def bounds(self, ) -> Tuple[float]:
        return 0, len(self.categorical)

    def _transform(self, value: float) -> Any:
        return self.categorical[int(value)]


@dataclass
class _DistributionSettings:

    type: str
    params: Union[_UniformDist, _UniformSample]

    @property
    def params(self, ) -> Union[_UniformDist, _UniformSample]:
        return self._params

    @params.setter
    def params(self, kwargs) -> None:
        self._params = {
            'uniform sample': _UniformSample,
            'uniform': _UniformDist
        }[self.type](**kwargs)

    @property
    def bounds(self, ) -> Tuple[float, float]:
        return self.params.bounds

    def transform(self, value: float) -> Any:
        return self.params.transform(value)

    @property
    def sa_value(self, ) -> Any:
        return self.params.sa_value


@dataclass
class _GeneratorArguments:
    common_parameters: Any


@dataclass
class _ArgumentHolder:
    args: list = None
    kwargs: dict = None


@dataclass
class _Generator:

    function: str
    output_name: str
    passed_to_simulation: bool
    arguments: dict

    @property
    def arguments(self, ) -> _ArgumentHolder:
        # return self._args
        return self._args

    @arguments.setter
    def arguments(self, val: dict):
        self._args = _ArgumentHolder(**val)

    @property
    def args(self, ) -> list:
        return self._args.args

    @property
    def kwargs(self, ) -> dict:
        return self._args.kwargs


class _SensitivityAnalysisVariable:

    def __init__(self, name, variable_name, distribution, type, generator=None) -> None:
        self.name: str = "_".join([name, variable_name])
        self.type: str = type
        self.distribution: _DistributionSettings = _DistributionSettings(
            type=distribution['type'], params=distribution['params'])


    def transform(self, val):
        self.distribution.transform(val)

    def _find_self(self, generator: dict):
        for key, value in generator.items():
            if isinstance(value, dict):
                self._find_self(value)
            elif self._check_name(value):
                generator[key] = self

    def _check_name(self, value: str) -> bool:
        if isinstance(value, str):
            return value in self.name
        return False


class SensitivityAnalysisGroup:

    """ Everything is at least a group. It becomes a variable if the correct parameters are present"""

    def __init__(self, name, **kwargs) -> None:

        # self.generator = generator
        self._variables = []

        self.name = name
        self.variables: List[_SensitivityAnalysisVariable] = kwargs

        self._generator: Union[_Generator,
                               None] = self._create_generator(**kwargs)

        # try to create the generator
        if 'generator_arguments' in kwargs.keys():
            self.generator_arguments: Union[None, _GeneratorArguments] = _GeneratorArguments(
                **kwargs['generator_arguments'])
        else:
            self.generator_arguments: Union[None, _GeneratorArguments] = None

    def _create_generator(self, **kwargs) -> Union[_Generator, None]:
        for key, value in kwargs.items():
            if key == 'generator':
                for i_key, i_value in value.items():
                    if i_key == "arguments":
                        if 'args' in i_value.keys():
                            for i, arg in enumerate(i_value['args']):
                                i_value['args'][i] = self._replace_name_with_reference(
                                    arg)
                        if 'kwargs' in i_value.keys():
                            for ii_key, ii_value in i_value['kwargs'].items():
                                i_value['kwargs'][ii_key] = self._replace_name_with_reference(
                                    ii_value)
                return _Generator(**value)

    def _replace_name_with_reference(self, name: str) -> object:
        for var in self._variables:
            if isinstance(name, str) and name in var.name:
                return var
        return name

    @property
    def variables(self, ):
        pass

    @variables.setter
    def variables(self, d: dict):
        try:
            self._variables.append(
                _SensitivityAnalysisVariable(name=self.name, **d)
            )
        except TypeError:
            for name, items in d.items():
                if name != 'generator' and isinstance(items, dict):
                    if 'variable_name' in items.keys():
                        self._variables.append(
                            _SensitivityAnalysisVariable(name=self.name, **items))
                    else:
                        self._variables.append(
                            SensitivityAnalysisGroup(name=name, **items))

    @variables.getter
    def variables(self, ):
        l = []
        for var_obj in self._variables:
            if isinstance(var_obj, _SensitivityAnalysisVariable):
                l.append(var_obj)
            else:
                l.extend(var_obj.variables)
        return l

    @property
    def generator(self, ):
        return self._generator


@dataclass
class _SensitivityAnalysisOutput:

    module: str
    arguments: dict
    
    @property
    def arguments(self, ) -> _ArgumentHolder:
        # return self._args
        return self._args
    
    @arguments.setter
    def arguments(self, val: dict):
        self._args = _ArgumentHolder(**val)


class _SensitivityAnalysisSettings:

    def __init__(self, d: dict) -> None:
        self._variables: List[SensitivityAnalysisGroup] = self._compose_variables(
            d['variables'])

        self.names: str = [v.name for v in self.variables]

        self.output: _SensitivityAnalysisOutput = _SensitivityAnalysisOutput(
            **d['Output']
            )
        self.num_runs: int = d['num_runs']
        self.working_root: str = d['working_root']

    def _compose_variables(self, d: dict, l=[]) -> List[_SensitivityAnalysisVariable]:
        for name, variable_d in d.items():
            if isinstance(variable_d, dict):
                # if 'variable_name' in variable_d.keys():
                l.append(
                    SensitivityAnalysisGroup(name, **variable_d)
                )
        return l

    @property
    def variable_num(self, ) -> int:
        return len(self.variables)

    @property
    def variables(self, ) -> List[_SensitivityAnalysisVariable]:
        l = []
        for var in self._variables:
            if isinstance(var, SensitivityAnalysisGroup):
                l.extend(var.variables)
            else:
                l.append(var)
        return l


@dataclass
class _FunctionArguments:
    kwargs: dict = None


@dataclass
class _SimFunctionCore:
    module: str
    arguments: _FunctionArguments = None
    path: str = None

    @property
    def arguments(self, ) -> _FunctionArguments:
        return self._arguments

    @arguments.setter
    def arguments(self, kwargs: dict):
        self._arguments = _FunctionArguments(**kwargs) if kwargs else None


@dataclass
class _SimulationCore:
    preprocessing: str
    cpu_cores: int
    manager_function: _SimFunctionCore
    simulation_function: _SimFunctionCore
    # arguments: str

    @property
    def manager_function(self, ) -> _SimFunctionCore:
        return self._manager_function

    @manager_function.setter
    def manager_function(self, kwargs: dict):
        self._manager_function = _SimFunctionCore(**kwargs)

    @property
    def simulation_function(self, ) -> _SimFunctionCore:
        return self._simulation_function

    @simulation_function.setter
    def simulation_function(self, kwargs: dict):
        self._simulation_function = _SimFunctionCore(**kwargs)


@dataclass
class _Metadata:
    name: str
    author: str


@dataclass
class _Settings:

    @property
    def metadata(self, ) -> _Metadata:
        return self._metadata

    @metadata.setter
    def metadata(self, d: dict) -> None:
        self._metadata = _Metadata(**d)

    @property
    def sensitivity_analysis(self, ) -> _SensitivityAnalysisSettings:
        return self._sensitivity_analysis

    @sensitivity_analysis.setter
    def sensitivity_analysis(self,  d: dict) -> dict:
        self._sensitivity_analysis = _SensitivityAnalysisSettings(d)

    @property
    def simulation_core(self, ) -> _SimulationCore:
        return self._simulation_core

    @simulation_core.setter
    def simulation_core(self,  d: dict) -> dict:
        self._simulation_core = _SimulationCore(**d)

    @property
    def file_manager(self, ) -> dict:
        return self._simulation_core

    @file_manager.setter
    def file_manager(self,  d: dict) -> dict:
        self._file_manager = d


class Settings4SASUMO(_Settings):

    def __init__(self, file_path: str) -> None:

        self._yaml_settings_path = file_path

        with open(file_path, 'r') as f:
            self._unpack_settings(yaml.safe_load(f))

    # def __getattribute__(self, name: str) -> Any:
    #     return self._settings[name]

    def _unpack_settings(self, d):
        self.metadata = d['Metadata']
        self.sensitivity_analysis = d['SensitivityAnalysis']
        self.simulation_core = d['SimulationCore']

    def save_myself(self, file_location: str):
        """
        Copy the input file to the location that the simulation is ran from. 
        
        Also refered to as the "Working Root"

        Args:
            file_location (str): [description]
        """
        file_name = os.path.split(self._yaml_settings_path)[1]
        # TODO: move the file correctly
        shutil.copy(self._yaml_settings_path, os.path.join(file_location, file_name))

    # def _read


if __name__ == "__main__":

    import os
    ROOT = os.path.dirname(os.path.abspath(__file__))
    s = Settings4SASUMO(os.path.join(
        ROOT, '../../', 'input_files', 'test.yaml'))
    print(s.simulation_core)
