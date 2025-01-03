from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class AnalysisMixin:
    @report_step()
    def descriptive_statistics(self: T, method=None):
        pass

    @report_step()
    def pairwise_correlations_numerical(self: T, method=None):
        pass


    @report_step()
    def evaluate_distribution_target(self: T, method=None):
        pass


    @report_step()
    def evaluate_distribution_features(self: T, method=None):
        pass
