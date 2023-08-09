import os
from dataclasses import dataclass

import click
import json5 as json
import pandas as pd
from joblib import Parallel, delayed

from SASUMO.functions.per_phase_delay import E3SimulationMetrics
from SASUMO.functions.simulation_metrics import SimulationMetrics
from tools.output_tools import USDOTCalibration

CAL_KEYS = [
    "_".join([key, movement, sigma])
    for key in ["63082002", "63082003", "63082004"]
    for movement in ["WB", "EB"]
    for sigma in ["sigma_1", "sigma_1.96"]
]

CAL_KEYS_EXTENDED = [
    "_".join([key, movement, sigma])
    for key in ["63082002", "63082003", "63082004"]
    for movement in ["WB", "EB", "4"] + (["8"] if key != "63082002" else [])
    for sigma in ["sigma_1", "sigma_1.96"]
]


@dataclass
class FileHandler:
    root: str

    @property
    def problem(
        self,
    ):
        return os.path.join(self.root, "SALib_Problem.json")

    @property
    def results_csv(
        self,
    ):
        return os.path.join(self.root, "processed_results.csv")

    @property
    def sample_file(
        self,
    ):
        return os.path.join(self.root, "SALib_Samples.txt")


def gen_import_func(parameter_sweep: bool):

    if parameter_sweep:
        from SASUMO.params import ParameterSweepConf as Conf
    else:
        from SASUMO.params import SASUMOConf as Conf

    def import_data(
        _dir_name,
        _dir,
    ):
        try:
            with open(os.path.join(_dir, "f_out.txt"), "r") as f:
                f_out = f.read()
                try:
                    d = {"f_out": float(f_out), "sample_num": int(_dir_name)}
                except ValueError:
                    # I added the number of vehicles used in the simulation to the output file
                    f_out, veh_num = f_out.split(",")
                    d = {
                        "f_out": float(f_out),
                        "veh_num": float(veh_num),
                        "sample_num": int(_dir_name),
                    }
        except Exception as e:
            raise f"issue with {_dir}" from e

        d |= {
            # load the variable values
            **Conf.var_2_records(os.path.join(_dir, "params.yaml")),
            # load the calibration data
            **USDOTCalibration.load_calibration_data(
                os.path.join(_dir, "calibration_results.json"), load_all=True
            ),
            # load the simulation metrics
            **SimulationMetrics.load_traffic_metrics(
                os.path.join(_dir, "simulation_metrics.json")
            ),
            # load the per-phase
            **E3SimulationMetrics.load_traffic_metrics(
                os.path.join(_dir, "per_phase_delay.json")
            ),
        }

        return d

    return import_data


def prepare_df(df: pd.DataFrame) -> pd.DataFrame:

    from tools.output_tools import FuelProperties

    df["Fuel_Gal"] = FuelProperties.joule_2_gal_gas(
        df["f_out"].values * 1e6
    )  # this value is in MJ

    for key in CAL_KEYS:
        if "63082004-EB" not in key:
            res = 0.95 - df[key] if "1.96" in key else 0.666 - df[key]
            res[res < 0] = 0
            df[f"{key}_score"] = 1 - res
        else:
            df[f"{key}_score"] = 1

    df["cal_score"] = df[[f"{key}_score" for key in CAL_KEYS]].mean(axis=1)
    df["Fuel_L"] = df["Fuel_Gal"] * 3.78541178
    df["cal_score_2"] = df[CAL_KEYS_EXTENDED].sum(axis=1)
    # df.drop([f"{key}_score" for key in CAL_KEYS], inplace=True, axis=1)
    return df


def prepare_df(
    df: pd.DataFrame, file_handler: FileHandler, parameter_sweep: bool
) -> pd.DataFrame:

    from tools.output_tools import FuelProperties

    df["Fuel_Gal"] = FuelProperties.joule_2_gal_gas(
        df["f_out"].values * 1e6
    )  # this value is in MJ

    for key in CAL_KEYS:
        if "63082004-EB" not in key:
            res = 0.95 - df[key] if "1.96" in key else 0.666 - df[key]
            res[res < 0] = 0
            df[f"{key}_score"] = 1 - res
        else:
            df[f"{key}_score"] = 1

    df["cal_score"] = df[[f"{key}_score" for key in CAL_KEYS]].mean(axis=1)
    df["Fuel_L"] = df["Fuel_Gal"] * 3.78541178
    df["cal_score_2"] = df[CAL_KEYS_EXTENDED].sum(axis=1)

    df.sort_index(
        inplace=True,
    )

    # replace string columns:
    if not parameter_sweep:
        problem = json.load(open(file_handler.problem, "r"))

        if any(df[problem["names"]].dtypes != "float64"):
            samples_df = pd.read_csv(
                file_handler.sample_file, sep=" ", names=problem["names"]
            )
            replace_columns = (
                df[problem["names"]]
                .columns[df[problem["names"]].dtypes != "float64"]
                .values
            )
            df[[f"{c}_conv" for c in replace_columns]] = df[replace_columns].copy()
            df[replace_columns] = samples_df[replace_columns].copy()
    return df


def find_incomplete(file_handler: FileHandler) -> bool:
    incomplete = []
    for _dir in os.scandir(file_handler.root):
        if not _dir.is_dir():
            continue
        if "f_out.txt" not in os.listdir(os.path.join(file_handler.root, _dir)):
            incomplete.append(_dir.name)
        else:
            with open(os.path.join(_dir.path, "f_out.txt"), "r") as f:
                if not f.read():
                    incomplete.append(_dir.name)
    if incomplete:
        print(f"{len(incomplete)} incomplete files")
        print("saving a list of incomplete files to incomplete.txt")
        with open(os.path.join(file_handler.root, "incomplete.txt"), "w") as f:
            f.write("\n".join(incomplete))
    return not incomplete


@click.command()
@click.argument("root", type=click.Path(exists=True))
@click.option("--smoke-test", is_flag=True, help="Only run a smoke test", default=False)
@click.option(
    "--parameter-sweep",
    is_flag=True,
    help="Indicates whether the folder is ",
    default=False,
)
def run(root: str, smoke_test: bool, parameter_sweep: bool) -> None:
    file_handler = FileHandler(root)

    # TODO this could be multithreaded and be quite a bit faster
    if not find_incomplete(file_handler):
        return

    # problem = json.load(open(file_handler.problem, "r"))
    if smoke_test:
        func = gen_import_func(parameter_sweep)
        results = [
            func(dir.name, dir.path)
            for dir in os.scandir(file_handler.root)
            if dir.is_dir()
        ]

    else:
        results = Parallel(n_jobs=os.cpu_count() - 1)(
            delayed(gen_import_func(parameter_sweep))(dir.name, dir.path)
            for dir in os.scandir(file_handler.root)
            if dir.is_dir()
        )

    results_df = pd.DataFrame.from_records(results, index="sample_num").sort_index()

    results_df = prepare_df(results_df, file_handler, parameter_sweep=parameter_sweep)
    print(f"Saving processed csv to {file_handler.results_csv}")
    results_df.to_csv(file_handler.results_csv)


if __name__ == "__main__":
    run()
