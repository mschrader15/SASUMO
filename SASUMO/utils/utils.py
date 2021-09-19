from importlib import import_module
import os
import csv
from lxml import etree
from xml.dom import minidom
import re
import mmap


def path_constructor(path: str, cwd: str = None) -> str:
    ''' Extract the matched value, expand env variable, and replace the match '''
    path_matcher = re.compile(r'\$\{([^}^{]+)\}')
    match = path_matcher.match(path)
    if match:
        env_var = match.group()[2:-1]
        if env_var == 'cwd':
            return cwd + path[match.end():]
        try:
            return os.environ.get(env_var) + path[match.end():]
        except TypeError:
            raise Exception(env_var)
    return path


def beefy_import(path: str) -> object:
    split_mod = path.split('.')
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
            'emissions': self._parse_and_write_emissions,
            #   'e1': parse_and_write_detector,
            #   'e2': parse_and_write_detector
        }[file_type]

    @staticmethod
    def _parse_and_write_emissions(elem, metadata):
        if (elem.tag in 'timestep') and (len(elem.attrib) > 0):
            meta_data = float(elem.attrib['time'])
            return meta_data, None
        elif (elem.tag in 'vehicle') and (len(elem.attrib) >= 19):
            elem_d = dict(elem.attrib) 
            elem_d['time'] = metadata
            return metadata, elem_d
        return metadata, None

    def process(self, ):
        yield from self.fast_iter(etree.iterparse(self._file_path, events=("start", "end")))

    def fast_iter(self, context, ):
        meta_data = 0
        for _, elem in context:
            meta_data, elem_d = self._parse_function(
                elem, metadata=meta_data)
            if elem_d:
                yield elem_d
            elem.clear()
            while elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    break


def on_disk_xml_parser(xml_path: str, file_type: str) -> list:
    yield from Parser(file_path=xml_path,
                      file_type=file_type).process()


class FleetComposition:

    def __init__(self, distribution_dictionary: dict, seed: int, route_file: str):

        import random

        self._random = random
        self._random.seed(seed)

        self._dist = []
        
        for name, percentage in distribution_dictionary.items():
            self._dist.extend(int(100 * percentage) * [name])

        self._r = route_file

    def _sample(self, ):

        return self._random.sample(self._dist, 1)[0]

    def replace_vehType(self, output_path=None):


        t = minidom.parse(self._r)

        for route_type in ["flow", "trip", "vehicle"]:
            for node in t.getElementsByTagName(route_type):
                self._replace_veh_type(node, )

        with open(self._r if not output_path else output_path, 'w') as f:
            f.write(t.toxml())

    def _replace_veh_type(self, element: minidom.Element) -> None:
        if element.hasAttribute("type"):
            element.setAttribute("type", self._sample())


def regex_fc_total(file_path, time_low: float=None, time_high: float =None):
    pattern = br'(fuel="[\d\.]*")'
    fc_t = 0
    with open(file_path, 'r+') as f:
        data = mmap.mmap(f.fileno(), 0)
        time_low_i = re.search("time=\"{}\"".format("{:.2f}".format(time_low)).encode(), data).span()[-1] if time_low else 0
        time_high_i = re.search("time=\"{}\"".format("{:.2f}".format(time_high)).encode(), data).span()[0] if time_high else -1

        for match in re.finditer(pattern, data[time_low_i:time_high_i]):
            fc = float(match.group(1).decode().split('=')[-1][1:-1])
            fc_t += fc
        del data
    return fc_t

# Below matches a whole vehicle row
# (<vehicle)(.)+(?=>)

if __name__ == "__main__":


    r = FleetComposition({'Class8Truck': 0.0, 'PersonalCar': 1}, 
                         seed=22, 
                         route_file='/home/max/remote/airport-harper-sumo/sumo-xml/sasumo-xml/route-file/route.in.xml')

    r.replace_vehType()

#     import time

#     t0 = time.time()
    
# #     total_fuel = 0
# #     for row in on_disk_xml_parser(xml_path="/home/max/tmp/airport_harper_sumo_sasumo/test/2021_08_26-08_59_49/sample_0/__temp__emissions.out.xml", file_type='emissions'):
# #         total_fuel += float(row['fuel'])
    
# #     print(total_fuel * 0.1)

#     fc_t = regex_fc_total("/home/max/tmp/airport_harper_sumo_sasumo/test/2021_08_26-08_59_49/sample_0/__temp__emissions.out.xml", time_low=3000, time_high=6000)

#     print("fc_t: ", fc_t)

#     print(f"time: {time.time() - t0}")

