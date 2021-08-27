from utils import path_constructor
from utils import regex_fc_total


class _OutputHandler:
    
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

    # def _load_xml(self):
    #     yield from on_disk_xml_parser(self._emissions_xml, file_type="emissions")

    def _y(self, ):
        return regex_fc_total(self._emissions_xml, self._time_filter_lower, self._time_filter_upper) * self._sim_step

    def matlab_fc_handler(self, ):
        """
        Here would go the consolidator of matlab fc output
        """
        pass