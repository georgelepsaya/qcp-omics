from typing import Optional, TypeVar, Literal, Union
import pandas as pd
from qcp_omics.report_generation.report_step import report_step
from qcp_omics.utils.protocols import HasData

T = TypeVar("T", bound=HasData)

class AnalysisMixin:
    """
    A mixin class providing analysis methods for descriptive statistics,
    pairwise correlations, and distribution evaluations for numerical data.
    """

    @report_step(output=True)
    def descriptive_statistics(self: T, method: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Generate descriptive statistics for the numerical data, including kurtosis and skewness.

        Args:
            method (Optional[str]): Placeholder for future extensions, currently unused.

        Returns:
            Optional[pd.DataFrame]: A DataFrame with descriptive statistics, or None if no numerical data is available.
        """
        if self.data_numerical is None or self.data_numerical.empty:
            return None

        # Compute basic statistics
        basic_stats = self.data_numerical.describe(include="all").T
        basic_stats["kurtosis"] = self.data_numerical.kurt()
        basic_stats["skewness"] = self.data_numerical.skew()

        return basic_stats

    @report_step(output=True)
    def pairwise_correlations_numerical(
        self: T, method: Literal["pearson", "spearman"] = "pearson"
    ) -> Optional[dict[str, Union[pd.DataFrame, object]]]:
        """
        Compute pairwise correlations for numerical data using the specified method and generate a heatmap.

        Args:
            method (Literal["pearson", "spearman"]): The correlation method to use. Defaults to "pearson".

        Returns:
            Optional[dict[str, Union[pd.DataFrame, object]]]:
                A dictionary containing the correlation matrix and heatmap object, or None if no numerical data is available.
        """
        if self.data_numerical is None or self.data_numerical.empty:
            return None

        # Compute correlation matrix
        corr_matrix = self.data_numerical.corr(method=method)

        # Generate heatmap (assumes self._heatmap is implemented in the parent class)
        heatmap = self._heatmap(corr_matrix)

        return {
            "corr_matrix": corr_matrix,
            "heatmap": heatmap
        }

    @report_step(output=True)
    def evaluate_distribution_features(self: T, method: Optional[str] = None) -> Optional[dict[str, object]]:
        """
        Evaluate the distribution of numerical features by generating histograms.

        Args:
            method (Optional[str]): Placeholder for future extensions, currently unused.

        Returns:
            Optional[dict[str, object]]: A dictionary containing histogram plots, or None if no numerical data is available.
        """
        if self.data_numerical is None or self.data_numerical.empty:
            return None

        # Generate histograms (assumes self._histograms is implemented in the parent class)
        hist_plots = self._histograms(self.data_numerical)

        return {
            "hist_plots": hist_plots
        }
