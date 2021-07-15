import csv
from lxml import etree

# FIELD_NAMES = {
#     'emissions': [
#         'timestep_time', 'vehicle_CO', 'vehicle_CO2', 'vehicle_HC',
#         'vehicle_NOx', 'vehicle_PMx', 'vehicle_angle', 'vehicle_eclass',
#         'vehicle_electricity', 'vehicle_fuel', 'vehicle_id', 'vehicle_lane',
#         'vehicle_noise', 'vehicle_pos', 'vehicle_route', 'vehicle_speed',
#         'vehicle_type', 'vehicle_waiting', 'vehicle_x', 'vehicle_y'
#     ],
#     'e1': [
#         'interval_begin', 'interval_end', 'interval_flow',
#         'interval_harmonicMeanSpeed', 'interval_id', 'interval_length',
#         'interval_nVehContrib', 'interval_nVehEntered', 'interval_occupancy'
#     ],
#     'e2': [
#         'interval_begin',
#         'interval_end',
#         'interval_id',
#         'interval_sampledSeconds',
#         'interval_nVehEntered',
#         'interval_nVehLeft',
#         'interval_nVehSeen',
#         'interval_meanSpeed',
#     ]
# }


def parse_and_write_emissions(elem, metadata):
    if (elem.tag in 'timestep') and (len(elem.attrib) > 0):
        meta_data = elem.attrib['time']
        return meta_data, False
    elif (elem.tag in 'vehicle') and (len(elem.attrib) >= 19):
        elem.attrib.update({'time': metadata})
        return metadata, True
    return None, False


PARSE_FUNCTION = {
    'emissions': parse_and_write_emissions,
    #   'e1': parse_and_write_detector,
    #   'e2': parse_and_write_detector
}


class Parser:
    def __init__(
        self,
        file_path,
        # xml_fields,
        parse_function,
    ):
        self._csv_writer = None
        self._file_path = file_path
        # self._fields_simp = xml_fields
        self._parse_function = parse_function
        
    def process(self, ):    
        yield from self.fast_iter(etree.iterparse(self._file_path, events=("start", "end")))

    def fast_iter(self, context, ):
        meta_data = 0
        for _, elem in context:
            meta_data, share_ok = self._parse_function(elem, metadata=meta_data)
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
                      parse_function=PARSE_FUNCTION[file_type]).process()


if __name__ == "__main__":

        for row in on_disk_xml_parser(xml_path="/home/max/SUMO/airport-harper-sumo/sumo-xml/emissions/emissions.out.xml", file_type='emissions'):
            print(row)