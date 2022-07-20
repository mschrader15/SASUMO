import os
from typing import Any, Tuple, Dict
import json5
import pint
import pandas as pd
from sumolib.xml import parse_fast

ureg = pint.UnitRegistry()


class E3SimulationMetrics:
    COLUMNS = [
        "begin",
        "end",
        "id",
        "meanTravelTime",
        "meanOverlapTravelTime",
        "meanSpeed",
        "meanHaltsPerVehicle",
        "meanTimeLoss",
        "vehicleSum",
        "meanSpeedWithin",
        "meanHaltsPerVehicleWithin",
        "meanDurationWithin",
        "vehicleSumWithin",
        "meanIntervalSpeedWithin",
        "meanIntervalHaltsPerVehicleWithin",
        "meanIntervalDurationWithin",
        "meanTimeLossWithin",
    ]

    def __init__(self, *args, **kwargs) -> None:
        self._args: Tuple = args or []
        self._kwargs: Dict[str, Any] = kwargs or {}

    def main(
        self,
    ) -> None:
        self._calculate_traffic_metrics(
            *self._args,
            **self._kwargs,
        )

    @staticmethod
    def load_traffic_metrics(file_path: str) -> dict:
        """
        Loads the simulation metrics from a file. Flattens the dictionary and returns it.
        """
        with open(file_path, "r") as f:
            return pd.json_normalize(json5.load(f,), sep="_").to_dict(
                orient="records"
            )[0]

    @staticmethod
    def _calculate_traffic_metrics(
        e3_output_file: os.PathLike,
        output_file_path: os.PathLike,
        warmup_time: float,
    ) -> None:
        """
        Ugly code. Copy paste from Jupyter notebook.

        Args:
            trip_info_file (os.PathLike): _description_
            output_file_path (os.PathLike): _description_
        """
        # read in the trip info file
        df = pd.DataFrame.from_records(iter(parse_fast(e3_output_file, 'interval', E3SimulationMetrics.COLUMNS)), columns=E3SimulationMetrics.COLUMNS).astype(
                {c: 'float' for c in E3SimulationMetrics.COLUMNS if c != 'id'}
            )


        df.sort_values("begin", inplace=True)
        df['TL'] = df['id'].apply(lambda x: x.split("_")[1])
        df['Phase'] = df['id'].apply(lambda x: x.split("_")[2])
        df = df.loc[df["begin"] > warmup_time].reset_index().copy()

        # get all the others
       ## How to Save this Data.....
        results = {}
        # for name, filt in zip(["EB", "WB", 'Other', "All"], [ebs, wbs, ~(ebs | wbs), [True] * len(df)]):
        for tl, _df in df.groupby("TL"):
            results[tl] = {
                phase: {
                    "meanTimeLoss": _df_phase.loc[_df_phase["meanTimeLoss"] > -1, "meanTimeLoss"].mean(),
                    "meanSpeed": _df_phase.loc[_df_phase["meanSpeed"] > -1, "meanSpeed"].mean(),
                    "meanHaltsPerVehicle": _df_phase.loc[_df_phase["meanHaltsPerVehicle"] > -1, "meanHaltsPerVehicle"].mean(),
                    "totalTimeLoss": (
                        _df_phase.loc[_df_phase["meanTimeLoss"] > -1, "meanTimeLoss"] * _df_phase["vehicleSum"]
                    ).sum(),
                    "timeLoss95th": (
                        _df_phase.loc[_df_phase["meanTimeLoss"] > -1, "meanTimeLoss"] * _df_phase["vehicleSum"]
                    ).quantile(0.95),
                }
                for phase, _df_phase in _df.groupby("Phase")
            }

            results[tl]["total"] = {
                "meanTimeLoss": _df.loc[_df["meanTimeLoss"] > -1, "meanTimeLoss"].mean(),
                "meanSpeed": _df.loc[_df["meanSpeed"] > -1, "meanSpeed"].mean(),
                "meanHaltsPerVehicle": _df.loc[_df["meanHaltsPerVehicle"] > -1, "meanHaltsPerVehicle"].mean(),
                "totalTimeLoss": (
                    _df.loc[_df["meanTimeLoss"] > -1, "meanTimeLoss"] * _df["vehicleSum"]
                ).sum(),
            }
            # for column in columns:
            # results[tl][phase][column]  _df_phase[column].mean()

        # save the results to a json
        with open(output_file_path, "w") as f:
            json5.dump(results, f, quote_keys=True, indent=4, trailing_commas=False)

