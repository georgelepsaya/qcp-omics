from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar, Literal
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class AnalysisMixin:
    @report_step(output=True)
    def descriptive_statistics(self: T, method=None):
        if self.data_numerical is None or len(self.data_numerical.columns) == 0:
            return

        basic_stats = self.data_numerical.describe(include='all').T

        basic_stats['kurtosis'] = self.data_numerical.kurt()
        basic_stats['skewness'] = self.data_numerical.skew()

        return basic_stats


    @report_step(output=True)
    def pairwise_correlations_numerical(self: T, method: Literal["pearson", "spearman"] = "pearson"):
        if self.data_numerical is None or len(self.data_numerical) == 0:
            return

        corr_matrix = self.data_numerical.corr(method=method)
        heatmap = self._heatmap(corr_matrix)

        return {
            "corr_matrix": corr_matrix,
            "heatmap": heatmap
        }


    @report_step(output=True)
    def evaluate_distribution_features(self: T, method=None):
        if self.data_numerical is None or len(self.data_numerical) == 0:
            return

        hist_plots = self._histograms(self.data_numerical)
        return {
            "hist_plots": hist_plots
        }
