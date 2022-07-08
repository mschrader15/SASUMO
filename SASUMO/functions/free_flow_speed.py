from typing import Dict, List

import json5 as json
from datetime import datetime, timedelta
import pandas as pd
from sumolib.xml import parse_fast_nested
from sumolib.shapes.polygon import read
from shapely.geometry import Polygon, Point


# Read in the XML File
def _read_polygons(radar_shape_file: str) -> list:
    """
    Reads in the XML file and returns a list of dictionaries.
    """
    return [(poly.id, Polygon(poly.shape)) for poly in read(radar_shape_file)]


def _box_finder(row: pd.DataFrame, polygons: list) -> str:
    # sourcery skip: use-next
    for poly_id, poly in polygons:
        if poly.contains(Point(row["x"], row["y"])):
            return poly_id
    return "unknown"


def _read_fcd_output(fcd_output_file: str) -> pd.DataFrame:
    """
    Reads in the FCD output file and returns a pandas dataframe.
    """
    return pd.DataFrame.from_records(
        (
            (timestep.time, *vehicle)
            for timestep, vehicle in parse_fast_nested(
                fcd_output_file,
                "timestep",
                ["time"],
                "vehicle",
                ["id", "x", "y", "speed", "pos", "lane"],
            )
        ),
        columns=["time", "id", "x", "y", "speed", "pos", "lane"],
    )


def _cleanup_df(
    df: pd.DataFrame, start_time: datetime, polygons: List[Polygon]
) -> pd.DataFrame:
    df["time"] = df["time"].apply(lambda x: start_time + timedelta(seconds=float(x)))
    df["edge"] = df["lane"].apply(lambda x: x[: x.rfind("_")])
    df[["pos", "speed", "x", "y"]] = df[["pos", "speed", "x", "y"]].astype("float")
    df["zone"] = df.apply(_box_finder, axis=1, polygons=polygons)
    return df


def _zone_data(df: pd.DataFrame) -> pd.DataFrame:
    zone_data = {
        name: _df.sort_values("time").copy() for name, _df in df.groupby("zone")
    }
    del df
    return zone_data


def _filter_ids(zone_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    min_speed = 10
    maximum_diff = 5
    for name, _df in zone_data.items():
        veh_groups = _df.groupby("id")
        valid_ids = veh_groups.apply(
            lambda x: ((x.speed.max() - x.speed.min()) < maximum_diff)
            & (x.speed.min() > min_speed)
        )
        valid_ids = valid_ids[valid_ids].index
        zone_data[name] = _df.loc[_df["id"].isin(valid_ids)]
    return zone_data


def _calculate_average_speed(
    zone_data: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, float]]:
    average_speeds = {}
    for name, _df in zone_data.items():
        tmp = _df.groupby("id").mean()
        average_speeds[name] = {
            "mean": tmp.speed.mean(),
            "std": tmp.speed.std(),
            "max": tmp.speed.max(),
            "min": tmp.speed.min(),
        }
    return average_speeds


def _calculate_time_speed(
    zone_data: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, float]]:
    resample_period = "300S"
    # add in the summary metrics
    results = _calculate_average_speed(zone_data)
    for zone_id, zone_df in zone_data.items():
        time_speed = (
            zone_df.groupby("id")
            .aggregate({"speed": "mean", "time": "mean"})
            .set_index("time")
            .sort_index()
        )
        veh_avg = time_speed.resample(resample_period).mean()
        veh_avg["veh_counts"] = time_speed.resample(resample_period).count()
        results[zone_id]["time_based"] = json.loads(veh_avg.to_json())
    return results


def _save_values(results: Dict[str, Dict[str, float]], output_file: str):
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4, trailing_commas=False, quote_keys=True)


class FreeFlowSpeed:
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def main(
        self,
    ) -> None:
        self.calculate_free_flow_speed(*self._args, **self._kwargs)

    @staticmethod
    def speed_analysis_loader(path: str) -> Dict[str, float]:
        """
        Loads the simulation speed from a file. Flattens the dictionary and returns it.
        """
        with open(path, "r") as f:
            d = json.load(
                f,
            )

        for _, v in d.items():
            v.pop("time_based")

        return pd.json_normalize(d, sep="_").to_dict(orient="records")[0]

    @staticmethod
    def calculate_free_flow_speed(
        radar_shape_file: str, fcd_output_file: str, output_file: str, start_time: str
    ):
        _save_values(
            _calculate_time_speed(
                _filter_ids(
                    _zone_data(
                        _cleanup_df(
                            _read_fcd_output(fcd_output_file),
                            pd.to_datetime(start_time),
                            _read_polygons(radar_shape_file),
                        )
                    )
                )
            ),
            output_file,
        )


# if __name__ == "__main__":

#     calculate_free_flow_speed(
#         radar_shape_file=r"C:\Users\gle\Documents\airport-harper-sumo\sumo-xml\detectors\radar.polygon.add.xml",
#         fcd_output_file=r"C:\Users\gle\Documents\tmp\airport-harper-sumo-output\TravelTimeTester\2022_06_30-06_22_46\fcd.out.xml",
#         output_file=r"C:\Users\gle\Documents\tmp\airport-harper-sumo-output\TravelTimeTester\2022_06_30-06_22_46\freeflow_speed.json",
#         start_time="2020-02-24T05:00:00",

#     )
