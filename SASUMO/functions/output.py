import os
from SASUMO.utils import path_constructor
from SASUMO.utils import regex_fc_total


class _OutputHandler:
    def __init__(self, cwd, *args, **kwargs) -> None:
        self._cwd = cwd

    @property
    def y(self):
        return self._y()

    def _y(
        self,
    ):
        pass

    def save_output(self, val):
        with open(os.path.join(self._cwd, "f_out.txt"), "w") as f:
            f.write(str(val))


class TotalEmissionsHandler(_OutputHandler):
    def __init__(
        self,
        cwd: str,
        emissions_xml: str,
        output_time_filter_lower: float,
        output_time_filter_upper: float,
        sim_step: float,
        save_output: bool = False,
    ) -> None:

        super().__init__(cwd)

        self._emissions_xml = path_constructor(emissions_xml, self._cwd)
        self._time_filter_lower = output_time_filter_lower
        self._time_filter_upper = output_time_filter_upper
        self._sim_step = sim_step
        self._save_output = save_output

    def _y(
        self,
    ):
        output = (
            regex_fc_total(
                self._emissions_xml, self._time_filter_lower, self._time_filter_upper
            )
            * self._sim_step
        )
        if self._save_output:
            self.save_output(output)
        return output

    def matlab_fc_handler(
        self,
    ):
        """
        Here would go the consolidator of matlab fc output
        """
        pass
