from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar, Any
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class QCMixin:
    def _identify_missing_values(self: T, method=None) -> dict[Any, float]:
        missing_values = self.data.isnull().mean() * 100
        filtered_missing = {col: pct for col, pct in missing_values.items() if pct > 0}
        sorted_missing = dict(sorted(filtered_missing.items(), key=lambda item: item[1], reverse=True))
        return sorted_missing


    @report_step(dict_out=True)
    def identify_missing_values(self: T, method=None) -> dict[Any, float]:
        return self._identify_missing_values(method)


    @report_step(snapshot=True, dict_out=True)
    def handle_missing_values(self: T, method="impute_mean") -> dict[str, str]:
        to_impute = []
        to_drop = []
        miss_cols = self._identify_missing_values()
        for col, miss in miss_cols.items():
            if miss <= 0.3:
                to_impute.append(col)
            else:
                to_drop.append(col)
        # drop with miss > 30
        # categorical -> use mode
        # numerical -> use mean or other method


    @report_step(dict_out=True)
    def detect_outliers(self: HasData, method="IQR") -> dict[str, list[tuple]]:
        outliers = {}
        for col in self.data_numeric.columns:
            q1 = self.data_numeric[col].quantile(0.25)
            q3 = self.data_numeric[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers_mask = (self.data_numeric[col] < lower_bound) | (self.data_numeric[col] > upper_bound)
            col_outliers = self.data_numeric[col][outliers_mask]
            if not col_outliers.empty:
                outliers[col] = list(col_outliers.items())
        return outliers


    @report_step(snapshot=True)
    def handle_outliers(self: HasData, method="capping") -> None:
        pass
