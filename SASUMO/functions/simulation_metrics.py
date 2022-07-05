from dataclasses import dataclass
import os
import sys
import pathlib
from typing import Any, Tuple, Dict
import json5
import pint
import pandas as pd
from datetime import timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sumolib.xml import parse_fast_nested

ureg = pint.UnitRegistry()


class SimulationMetrics:
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
    def _calculate_traffic_metrics(
        trip_info_file: os.PathLike,
        output_file_path: os.PathLike,
        warmup_time: float,
        route_begin_ends: dict,
        diesel_filter: str = "lambda x: False",
    ) -> None:
        """
        Ugly code. Copy paste from Jupyter notebook.

        Args:
            trip_info_file (os.PathLike): _description_
            output_file_path (os.PathLike): _description_
        """
        # read in the trip info file
        df = (
            pd.DataFrame.from_records(
                (
                    (*tripinfo, *emissions)
                    for tripinfo, emissions in parse_fast_nested(
                        trip_info_file,
                        "tripinfo",
                        [
                            "id",
                            "depart",
                            "departLane",
                            "departDelay",
                            "arrival",
                            "arrivalLane",
                            "duration",
                            "routeLength",
                            "waitingTime",
                            "waitingCount",
                            "timeLoss",
                            "vType",
                        ],
                        "emissions",
                        ["fuel_abs"],
                    )
                ),
                columns=[
                    "id",
                    "depart",
                    "departLane",
                    "departDelay",
                    "arrival",
                    "arrivalLane",
                    "duration",
                    "routeLength",
                    "waitingTime",
                    "waitingCount",
                    "timeLoss",
                    "vType",
                    "fuel_abs",
                ],
            )
            .astype(
                {
                    "depart": float,
                    "departDelay": float,
                    "arrival": float,
                    "routeLength": float,
                    "waitingTime": float,
                    "waitingCount": float,
                    "timeLoss": float,
                    "fuel_abs": float,
                    "duration": float,
                }
            )
            .sort_values("depart")
        )

        df["departEdge"] = df["departLane"].apply(lambda x: x[: x.rfind("_")])
        df["arrivalEdge"] = df["arrivalLane"].apply(lambda x: x[: x.rfind("_")])
        df = df.loc[df["depart"] > warmup_time].reset_index().copy()

        route_filters = {
            route_name: ((df["departEdge"] == route_begin_end[0])
            & (df["arrivalEdge"] == route_begin_end[1])).values
            for route_name, route_begin_end in route_begin_ends.items()
        }

        # get all the others
        route_filters["other"] = (pd.DataFrame(route_filters)[route_filters.keys()].sum(axis=1) == 0).values
        route_filters["all"] = (df["departEdge"] != df["arrivalEdge"]).values  # aka all

        # calculate the fuel
        diesel_filter = eval(diesel_filter)
        df["fuel_MJ"] = 0
        diesel_filter = df["vType"].apply(diesel_filter)
        car_filter = ~ diesel_filter
        df.loc[diesel_filter, "fuel_MJ"] = (
            df.loc[diesel_filter, "fuel_abs"] * (1 / 1000) * (1 / 1000) * 42.8
        )  # mg * 1/1000 g/mg * 1/1000 kg/g * 42.8 MJ/kg
        df.loc[car_filter, "fuel_MJ"] = (
            df.loc[car_filter, "fuel_abs"] * (1 / 1000) * (1 / 1000) * 43.4
        )  # mg * 1/1000 g/mg * 1/1000 kg/g * 43.4 MJ/kg

        results = {
            name: {
                "total_vehicles": df.loc[filt, "id"].unique().shape[0],
                "travel_time": {
                    "total": df.loc[filt, "duration"].sum(),
                    "average": df.loc[filt, "duration"].mean(),
                    "quantile_95": df.loc[filt, "duration"].quantile(0.95),
                },
                "delay": {
                    "total": df.loc[filt, "timeLoss"].sum(),
                    "average": df.loc[filt, "timeLoss"].mean(),
                    "quantile_95": df.loc[filt, "timeLoss"].quantile(0.95),
                },
                "waiting_time": {
                    "total": df.loc[filt, "waitingTime"].sum(),
                    "average": df.loc[filt, "waitingTime"].mean(),
                    "quantile_95": df.loc[filt, "waitingTime"].quantile(0.95),
                    "avg_num_stops": df.loc[filt, "waitingCount"].mean(),
                },
                "fuel_energy": {
                    "total": df.loc[filt, "fuel_MJ"].sum(),
                    "average": df.loc[filt, "fuel_MJ"].mean(),
                    "quantile_95": df.loc[filt, "fuel_MJ"].quantile(0.95),
                },
                "speed_mps": {
                    "average": (
                        df.loc[filt, "routeLength"] / df.loc[filt, "duration"]
                    ).mean(),
                    "std": (
                        df.loc[filt, "routeLength"] / df.loc[filt, "duration"]
                    ).std(),
                    "quantile_95": (
                        df.loc[filt, "routeLength"] / df.loc[filt, "duration"]
                    ).quantile(0.95),
                },
            }
            for name, filt in route_filters.items()
        }  # do what number that 95% are less than.

        # save the results to a json
        with open(output_file_path, "w") as f:
            json5.dump(results, f, quote_keys=True, indent=4, trailing_commas=False)


# if __name__ == "__main__":

#     SimulationMetrics(
#     )._calculate_traffic_metrics(
#         trip_info_file="/home/max/tmp/sasumo-output/Distro_Width+Delta+Random_Seed/07.05.2022_15.15.36/0/__temp__tripinfo.out.xml",
#         output_file_path="traffic_metrics.json",
#         warmup_time=3600,
#         route_begin_ends={
#             "EB": ["834845345#1", "gneE14"],
#             "WB": ["115872656#4", "115872656#13.8"]
#         },
#         diesel_filter="lambda x: 'truck' in x",

#     )