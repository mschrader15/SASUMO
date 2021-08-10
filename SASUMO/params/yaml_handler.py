
from SASUMO.SASUMO.utils.utils import beefy_import
from typing import Any, List, Tuple, Union
import yaml
from dataclasses import dataclass


class _Dist:

    def transform(self, value: float) -> Any:
        return self._transform(value)

    def _transform(self, value: float) -> Any:
        return value


@dataclass
class _UniformDist(_Dist):
    min: float
    max: float

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

@dataclass
class _Generator:

    function: str
    arguments: Tuple


class _SensitivityAnalysisVariable:

    def __init__(self, variable_name, distribution, generator=None) -> None:
        self.name: str = variable_name
        self.distribution: _DistributionSettings = _DistributionSettings(type=distribution['type'], params=distribution['params'])
        self.generator: Union[_Generator, None] = _Generator(**generator) if generator else None

    # def _type_helper()

@dataclass
class _SensitivityAnalysisOutput:
    module: str


class _SensitivityAnalysisSettings:

    def __init__(self, d: dict) -> None:
        self.variables: List[_SensitivityAnalysisVariable] = self._compose_variables(d['variables'])
        self.names: str = [v.name for v in self.variables]
        self.output: _SensitivityAnalysisOutput = _SensitivityAnalysisOutput(**d['Output']) 
        self.num_runs: int = d['num_runs']
        self.working_root: str = beefy_import(d['working_root'])
        
    def _compose_variables(self, d: dict, l=[]) -> List[_SensitivityAnalysisVariable]:
        for _, variable_d in d.items():
            if isinstance(variable_d, dict):
                if 'variable_name' in variable_d.keys():
                    l.append(_SensitivityAnalysisVariable(**variable_d))
                else:
                    self._compose_variables(variable_d, l)
        return l
    
    @property
    def variable_num(self, ) -> int:
        return len(self.variables)


@dataclass
class _FunctionArguments:
    settings: str = None


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
class _Settings:

    @property
    def metadata(self, ) -> object:
        return self._metadata
    
    @metadata.setter
    def metadata(self, d: dict) -> None:
        self._metadata = d 
    
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
        
        with open(file_path, 'r') as f:
            self._unpack_settings(yaml.safe_load(f))

    # def __getattribute__(self, name: str) -> Any:
    #     return self._settings[name]
        
    def _unpack_settings(self, d):
        self.metadata = d['Metadata']
        self.sensitivity_analysis = d['SensitivityAnalysis']
        self.simulation_core = d['SimulationCore']


if __name__ == "__main__":
    
    import os
    ROOT = os.path.dirname(os.path.abspath(__file__))
    s = Settings4SASUMO(os.path.join(ROOT, '../../', 'input_files', 'test.yaml'))
    print(s.simulation_core)