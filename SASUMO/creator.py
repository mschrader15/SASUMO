# from SASUMO.SASUMO.functions.function import
import os
import random
import sys
from typing import List, Tuple

import click
import json5 as json
import numpy as np
import ray
# external imports
from SALib.analyze import sobol
from SALib.sample import saltelli

# internal imports
from SASUMO.params import Config
from SASUMO.utils import beefy_import, create_folder
from SASUMO.utils import constants as c


def _to_lognormal(mu, sd):
    import math

    lns = math.sqrt(math.log(sd / mu) ** 2 + 1)
    lnmu = math.log(mu) - 0.5 * math.log((sd / mu) ** 2 + 1)
    return lnmu, lns


class SASUMO:
    def __init__(self, yaml_file_path: str, rerun: bool = False, rerun_file: str = '') -> None:
        # instantate the Settings4SASUMO class
        self._settings = Config(yaml_file_path)

        # try to create the folder to work in.
        try:
            create_folder(self._settings.Metadata.output)
            self._folder_exists = False
        except FileExistsError:
            self._folder_exists = True
            if rerun:
                self._rerun = True
                with open(rerun_file, "r") as f:
                    self._rerun_list = f.read().splitlines(keepends=False)

        # save a copy of the settings file
        if not self._folder_exists:
            self._settings.to_yaml(
                os.path.join(self._settings.Metadata.output, "sasumo_params.yaml"),
                resolve=True,
            )

        # generate and save the problem definition
        self._problem = self._compose_problem()
        # TODO: Do I need to do this?
        self._save_problem()

        # generate the samples
        self._samples = self._generate_samples()
        if self._folder_exists:
            if not self._rerun:
                sp = self._find_start_point()
                self._sp = lambda x: sp + x
                print(f"[!] Starting from incomplete SA. Continuing from {self._sp(0)}")
                self._samples = self._samples[self._sp:]
            else:
                print(f"[!] Starting from incomplete SA. Continuing from {self._rerun_list[0]}")
                self._remove_incomplete(self._rerun_list)
                self._samples = [self._samples[int(s)] for s in self._rerun_list]
                self._sp = lambda x: int(self._rerun_list[x])  # the start point is the last rerun
        else:
            self._sp = lambda x: 0 + x  # the start point is 0

        # add the required paths to PYTHON PATH
        self._update_path()

        # import the desired module
        self._f = None
        self.main_fn_helper(self._settings.get("ManagerFunction").module)

    def main_fn_helper(self, module_path: str) -> None:
        """
        This is really just for debug mode. To override the "RemoteEmiss...."

        Args:
            module_path (str): [description]
        """
        self._f = beefy_import(module_path)

    def _update_path(
        self,
    ):

        for new_path in [
            self._settings.SimulationCore.get("ManagerFunction", {}).get("path", ""),
            self._settings.SimulationCore.SimulationFunction.get("path", ""),
        ]:
            if new_path:
                sys.path.append(new_path)

    def _remove_incomplete(self, incomplete_list) -> None:
        import shutil
        for dir in incomplete_list:
            shutil.rmtree(os.path.join(self._settings.Metadata.output, str(dir)))


    def _find_start_point(self) -> int:
        import shutil

        incomplete = [
            int(_dir.name)
            for _dir in os.scandir(self._settings.Metadata.output)
            # TODO: f_out is a hard code and will not work for others
            if _dir.is_dir() and "f_out.txt" not in os.listdir(_dir.path)
        ]
        incomplete.sort()
        if incomplete:
            sp = int(incomplete[0])
            if len(incomplete) > 1:
                for dir in range(sp, int(incomplete[-1]) + 1):
                    shutil.rmtree(os.path.join(self._settings.Metadata.output, str(dir)))
        else:
            sp = sorted((int(_dir.name) for _dir in os.scandir(self._settings.Metadata.output) if _dir.is_dir()), reverse=True)[0] + 1
        return sp

    def _generate_seed(
        self,
    ):
        # If the random seed is a part of the SA then we don't need them
        if self._settings.get("Variables", {}).get("RandomSeed", ""):
            return None
        return random.randint(a=0, b=c.SEED)

    def _generate_samples(
        self,
    ) -> np.array:
        if self._folder_exists:
            # load the samples from the file
            return np.loadtxt(
                os.path.join(self._settings.Metadata.output, c.SAMPLES_FILE_NAME)
            )

        if self._settings.get("mode", "") == "correlated":
            from SALib.sample import sobol_corr

            sample = sobol_corr.sample(
                self._problem,
                self._settings.get("N"),
            )

        else:
            sample = saltelli.sample(
                self._problem,
                int(self._settings.get("N")),
                calc_second_order=self._settings.get("calc_second_order", False),
            )

        print(f"Running {len(sample)} simulations")

        np.savetxt(
            os.path.join(self._settings.Metadata.output, c.SAMPLES_FILE_NAME),
            sample,
        )

        return sample

    def _compose_problem(
        self,
    ) -> dict:
        if self._folder_exists:
            with open(
                os.path.join(
                    self._settings.Metadata.output, c.PROBLEM_DESCRIPT_FILE_NAME
                ),
                "r",
            ) as f:
                return json.load(f)
        else:
            sa_vars = self._settings.get("Variables", {})
            return {
                "num_vars": len(sa_vars),
                "names": [
                    name
                    for name, var in sa_vars.items()
                ],
                "bounds": [
                    self._compose_bounds(var)
                    for var in sa_vars.values()
                ],
                "dists": [
                    var.get("sobol_dist", "unif")
                    for var in sa_vars.values()
                ],
                **(
                    {
                        "distrs": [
                            var.distr
                            for _, var in sa_vars.items()
                        ]
                    }
                    if self._settings.get("mode", "")
                    == "correlated"
                    else {}
                ),
                **(
                    {
                        "corr": [
                            var.corr
                            for _, var in sa_vars.items()
                        ]
                    }
                    if self._settings.get("mode", "")
                    == "correlated"
                    else {}
                ),
            }

    def _compose_bounds(self, variable_obj: object) -> Tuple[float, float]:
        """
        Used to generate the bounds for the simulation. Can be extended to support categoricals

        Args:
            variable_obj (object): An instance of a

        Returns:
            Tuple[float, float]:
        """
        if variable_obj.get("sobol_dist", "unif") == "unif":
            # return (variable_obj.distribution.get("min", 0), variable_obj.distribution.get("max", 1))
            try:
                return (
                    variable_obj.get(
                        "sobol_dist_params",
                    ).get("lb", 0),
                    variable_obj.get(
                        "sobol_dist_params",
                    ).get("ub"),
                )
            except (TypeError, AttributeError):
                return (
                    variable_obj.sumo_dist.params.get("lb", 0),
                    variable_obj.sumo_dist.params.ub,
                )
        elif variable_obj.get("sobol_dist", "unif") in [
            "norm",
        ]:
            return (
                variable_obj.sobol_dist_params.mean,
                variable_obj.sobol_dist_params.std,
            )
        elif variable_obj.get("sobol_dist", "unif") == "lognorm":
            return _to_lognormal(
                variable_obj.sobol_dist_params.mean, variable_obj.sobol_dist_params.std
            )

        raise NotImplementedError("This distribution is not supported")

    def _save_problem(
        self,
    ) -> None:
        if not self._folder_exists:
            with open(
                os.path.join(
                    self._settings.Metadata.output,
                    c.PROBLEM_DESCRIPT_FILE_NAME,
                ),
                "w",
            ) as f:
                f.write(
                    json.dumps(
                        self._problem,
                        indent=4,
                        quote_keys=True,
                        trailing_commas=False,
                    )
                )

    def main(self, smoke_test=False) -> List[List[float]]:

        dispatch = []
        results = []

        num_parallel = min(self._settings.get("parallel_trials", os.cpu_count()), os.cpu_count(), len(self._samples))

        for i, _ in enumerate((range(2),) * 2 if smoke_test else self._samples):

            dispatch.append([i, self._spawn_process(i)])

            while len(
                dispatch
            ) >= num_parallel or (
                i >= (len(self._samples) - 1) and dispatch
            ):

                finished, _ = ray.wait(
                    [_id for _, _id in dispatch], num_returns=1, timeout=0.1
                )

                if len(finished):
                    j = 0
                    while dispatch[j][-1] != finished[0]:
                        j += 1
                    results.append(
                        [ray.get(dispatch[j][1]), dispatch.pop(j)[0]]
                    )  # results.append([[ray.get(_id), i] for i, _id in dispatch])

        return sorted(results, key=lambda x: x[1])

    def _spawn_process(self, index: int) -> ray.ObjectRef:

        p = self._f.remote(
            self._settings.generate_process(
                process_var=self._samples[index],
                process_id=str(self._sp(index)),
                random_seed=self._generate_seed(),
            )
        )
        # )
        return p.run.remote()

    def debug_main(
        self,
    ) -> None:

        index = 0

        self._f(
            yaml_params=self._settings.generate_process(
                process_var=self._samples[index],
                process_id=str(self._sp(index)),
                random_seed=self._generate_seed(),
            ),
        ).run()

    def save_results(self, sobol_analysis: list, results: list) -> None:
        # save the sobol analysis

        if not self._folder_exists:
        
            for i, result in enumerate(sobol_analysis.to_df()):
                result.to_csv(
                    os.path.join(self._settings.Metadata.output, c.SOBOL_ANALYSIS(i))
                )

            # save the results
            np.savetxt(
                os.path.join(self._settings.Metadata.output, c.RESULTS_NAME),
                np.array(results),
            )

    def analyze(self, results) -> dict:
        if not self._folder_exists:
            if self._settings.SensitivityAnalysis.get("mode", "") == "correlated":
                from SALib.analyze import sobol_corr

                return sobol_corr.analyze(
                    self._problem,
                    np.array([r[0] for r in results]),
                    self._settings.SensitivityAnalysis.N,
                )

            return sobol.analyze(
                self._problem, np.array([r[0] for r in results]), print_to_console=True
            )


@click.command()
@click.option(
    "--debug", is_flag=True, help="Run without Ray. For debugging simulations"
)
@click.option(
    "--smoke-test", is_flag=True, help="Run with Ray but for debugging simulations"
)
@click.option(
    "--finish-existing",
    is_flag=True,
    help="Finish a sensitivity analysis that quit for some reason. It will replay the last # - CPU * 2, just to be safe",
)
@click.option(
    "--rerun", is_flag=True, help="Re-run the sensitivity analysis for specified iterations"
)
@click.option(
    "--rerun-file", type=click.Path(exists=True), help="file of iterations to re-run, deliminated by newlines"
)
@click.option(
    "--parameter-sweep", is_flag=True, help="Run a parameter sweep",
)
@click.argument("settings_file", )
def run(debug, smoke_test, finish_existing, settings_file, rerun, rerun_file, parameter_sweep):

    if parameter_sweep:
        # this prevents the circular import error
        from SASUMO.parameter_sweep import ParameterSweep
        s = ParameterSweep(settings_file)
    else:
        s = SASUMO(settings_file, rerun, rerun_file)

    if debug:
        if "Remote" in s._settings.get("ManagerFunction").module:
            s._settings.get("ManagerFunction").module = s._settings.get(
                "ManagerFunction"
            ).module.replace("Remote", "")
            s.main_fn_helper(s._settings.get("ManagerFunction").module)
        s.debug_main()
    else:
        try:
            ray.init(address="auto")
        except (ConnectionError, RuntimeError):
            print("Starting Ray from python instead")
            # if smoke_test:
            # ray.init(local_mode=smoke_test)
            ray.init()

        results = s.main()

        analysis = s.analyze(results)

        s.save_results(analysis, results)


if __name__ == "__main__":

    run()
