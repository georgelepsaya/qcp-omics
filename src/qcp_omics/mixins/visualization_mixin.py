from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class VisualizationMixin:

    def histogram(self: T):
        pass


    def box_plot(self: T):
        pass


    def explained_variance(self: T):
        pass


    def pca_plot(self: T):
        pass


    def scatter_plot(self: T):
        pass


    def heatmap(self: T):
        pass
