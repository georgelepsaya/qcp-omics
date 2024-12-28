from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class AnalysisMixin:
    @report_step(snapshot=True)
    def descriptive_statistics(self: T, method=None):
        pass