from abc import ABCMeta
from utils import on_disk_xml_parser, path_constructor


class _OutputHandler:

    # def __new__(cls, *args, **kwargs):
    #     return super(_OutputHandler, cls).__new__(cls, *args, **kwargs)

    
    def __init__(self, *args, **kwargs) -> None:
        pass

    @property
    def y(self):
        return self._y()

    def  _y(self, ):
        pass


class TotalEmissionsHandler(_OutputHandler):
    
    def __init__(self, 
                 cwd: str, 
                 emissions_xml: str, 
                 output_time_filter_lower: float, 
                 output_time_filter_upper: float, 
                 sim_step: float) -> None:
        
        super(_OutputHandler, self).__init__()

        self._emissions_xml = path_constructor(emissions_xml, cwd)
        self._time_filter_lower = output_time_filter_lower
        self._time_filter_upper = output_time_filter_upper
        self._sim_step = sim_step

    def _load_xml(self):
        yield from on_disk_xml_parser(self._params['emissions_output'], file_type="emissions")

    def _y(self, ):
        iter_xml = self._load_xml()
        row = next(iter_xml)
        fc_total = []
        while row['time'] < self._time_filter_upper:
            if row['time'] > self._time_filter_lower:
                fc_total.append(row['fuel'])
            row = next(iter_xml)
        return sum(fc_total) * self._sim_step


        sim_step = self._params['sim_step']
        if self._params['fc_mode'].lower() == "sumo":
            return sum(float(row['fuel']) * sim_step for row in self._load_xml() 
                        if lower_time_b < row['time'] < upper_time_b)

    def matlab_fc_handler(self, ):
        """
        Here would go the consolidator of matlab fc output
        """
        pass