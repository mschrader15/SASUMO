from importlib import import_module
import os
import csv
from lxml import etree
from xml.dom import minidom
import re


def path_constructor(path: str, cwd: str = None) -> str:
    ''' Extract the matched value, expand env variable, and replace the match '''
    path_matcher = re.compile(r'\$\{([^}^{]+)\}')
    match = path_matcher.match(path)
    if match:
        env_var = match.group()[2:-1]
        if env_var == 'cwd':
            return cwd + path[match.end():]
        return os.environ.get(env_var) + path[match.end():]
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
            meta_data = elem.attrib['time']
            return meta_data, False
        elif (elem.tag in 'vehicle') and (len(elem.attrib) >= 19):
            elem.attrib.update({'time': metadata})
            return metadata, True
        return None, False

    def process(self, ):
        yield from self.fast_iter(etree.iterparse(self._file_path, events=("start", "end")))

    def fast_iter(self, context, ):
        meta_data = 0
        for _, elem in context:
            meta_data, share_ok = self._parse_function(
                elem, metadata=meta_data)
            if share_ok:
                yield elem.attrib
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


# if __name__ == "__main__":

    # r = RouteDistComber({'truck': 0.7, 'car': 0.3}, seed=22, route_file_path='/home/max/SUMO/airport-harper-sumo/sumo-xml/route-sampler/route_sampler.route.xml')

    # r.replace_vehType()

        # for row in on_disk_xml_parser(xml_path="/home/max/SUMO/airport-harper-sumo/sumo-xml/emissions/emissions.out.xml", file_type='emissions'):
        #     print(row)
