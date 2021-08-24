from abc import ABCMeta
from utils import on_disk_xml_parser 


class _OutputHandler(ABCMeta):
    
    def __init__(self, *args, **kwargs) -> None:
        pass

    @property
    def y(self):
        return self._y()

    def  _y(self, ):
        pass


class TotalEmissionsHandler(_OutputHandler):
    
    def __init__(self, emissions_xml) -> None:
        super(_OutputHandler, self).__init__()
        self._emissions_xml = params

    def _load_xml(self):
        yield from on_disk_xml_parser(self._params['emissions_output'], file_type="emissions")

    def _y(self, ):
        
        lower_time_b = self._params['output_time_filter_lower']
        upper_time_b = self._params['output_time_filter_upper']
        sim_step = self._params['sim_step']
        if self._params['fc_mode'].lower() == "sumo":
            return sum(float(row['fuel']) * sim_step for row in self._load_xml() 
                        if lower_time_b < row['time'] < upper_time_b)

    def matlab_fc_handler(self, ):
        """
        Here would go the consolidator of matlab fc output
        """
        pass