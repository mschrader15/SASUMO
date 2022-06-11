from importlib import import_module
import os
import csv
from tempfile import TemporaryFile
from lxml import etree
from xml.dom import minidom
import re
import mmap


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


def regex_fc_total(file_path, time_low: float = None, time_high: float = None):
    pattern = rb'(fuel="[\d\.]*")'
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
            fc = float(match.group(1).decode().split("=")[-1][1:-1])
            fc_t += fc
        del data
    return fc_t
