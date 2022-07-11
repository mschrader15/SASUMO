from importlib import import_module
import os
import csv
from tempfile import TemporaryFile
from typing import Callable
from lxml import etree
from xml.dom import minidom
import re
import mmap


SUMO_DIESEL_GRAM_TO_JOULE: float = 42.8e-3
SUMO_GASOLINE_GRAM_TO_JOULE: float = 43.4e-3


def create_folder(path, safe: bool = True) -> str:
    os.makedirs(path, exist_ok=not safe)
    return path


def beefy_import(path: str, internal: bool = True) -> object:
    if ("SASUMO" not in path) and internal:
        path = ".".join(["SASUMO", path])
    split_mod = path.split(".")
    return getattr(import_module(".".join(split_mod[:-1])), split_mod[-1])


class Parser:
    def __init__(
        self,
        file_path,
        # xml_fields,
        file_type,
    ):
        self._csv_writer = None
        self._file_path = file_path
        # self._fields_simp = xml_fields
        self._parse_function = {
            "emissions": self._parse_and_write_emissions,
        }[file_type]

    @staticmethod
    def _parse_and_write_emissions(elem, metadata):
        if (elem.tag in "timestep") and (len(elem.attrib) > 0):
            meta_data = float(elem.attrib["time"])
            return meta_data, None
        elif (elem.tag in "vehicle") and (len(elem.attrib) >= 19):
            elem_d = dict(elem.attrib)
            elem_d["time"] = metadata
            return metadata, elem_d
        return metadata, None

    def process(
        self,
    ):
        yield from self.fast_iter(
            etree.iterparse(self._file_path, events=("start", "end"))
        )

    def fast_iter(
        self,
        context,
    ):
        meta_data = 0
        for _, elem in context:
            meta_data, elem_d = self._parse_function(elem, metadata=meta_data)
            if elem_d:
                yield elem_d
            elem.clear()
            while elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    break


def on_disk_xml_parser(xml_path: str, file_type: str) -> list:
    yield from Parser(file_path=xml_path, file_type=file_type).process()

def regex_energy_total(
    file_path,
    sim_step: float,
    time_low: float = None,
    time_high: float = None,
    diesel_filter: str = None,
    gasoline_filter: str = None,
    x_filter: str = None,
    y_filter: str = None,
) -> float:
    """
    This function reads the emissions xml file and returns the total energy consumption in MJ in the time range.

    Diesel and gasoline filters are needed to calculate the energy consumption of diesel and gasoline separately. It is applied to the vehicles' emissions class

    Args:
        file_path: path to the emissions xml file
        sim_step: simulation step
        time_low: lower time bound
        time_high: upper time bound
        diesel_filter: function to filter diesel vehicles, as a string
        gasoline_filter: function to filter gasoline vehicles, as a string
    
    Returns:
        total energy consumption in MJ
    """
    diesel_filter = eval(diesel_filter) if diesel_filter else False
    gasoline_filter = eval(gasoline_filter) if gasoline_filter else False
    x_filter = eval(x_filter) if x_filter else False
    y_filter = eval(y_filter) if y_filter else False

    pattern = rb'eclass="\w+\/(\w+?)".+fuel="([\d\.]*)".+x="([\d\.]*)" y="([\d\.]*)"'
    fc_t = 0
    with open(file_path, "r+") as f:
        data = mmap.mmap(f.fileno(), 0)
        time_low_i = (
            re.search(
                'time="{}"'.format("{:.2f}".format(time_low)).encode(), data
            ).span()[-1]
            if time_low
            else 0
        )
        try:
            time_high_i = (
                re.search(
                    'time="{}"'.format("{:.2f}".format(time_high)).encode(), data
                ).span()[0]
                if time_high
                else -1
            )
        except AttributeError:
            # this means that the time high does not exist in the file so we count all the way to the end
            time_high_i = -1

        for match in re.finditer(pattern, data[time_low_i:time_high_i]):
            if (
               (not x_filter or (x_filter and x_filter(float(match[3]))))
                and (not y_filter or (y_filter and y_filter(float(match[4]))))
            ):
                fc = float(match[2]) / 1e3  # this is in mg/s * 1 / 1000 g/mg
                if diesel_filter or gasoline_filter:
                    if gasoline_filter(match[1].decode()):
                        fc *= SUMO_GASOLINE_GRAM_TO_JOULE
                    elif diesel_filter(match[1].decode()):
                        fc *= SUMO_DIESEL_GRAM_TO_JOULE
                    else:
                        raise ValueError("The filter did not match any of the classes")
                fc_t += fc
        del data
    return fc_t * sim_step  # output is in MJ
