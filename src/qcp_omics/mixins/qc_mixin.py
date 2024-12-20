from qcp_omics.report_generation.report_step import report_step
import typing as t
from qcp_omics.utils.protocols import HasData


class QCMixin:
    @report_step(snapshot=True)
    def identify_missing_values(self: HasData) -> dict[t.Any, float]:
        missing_values = self.data.isnull().mean() * 100
        missing = {col: pct for col, pct in missing_values.items() if pct > 0}
        return missing


    @report_step(snapshot=False, dict_out=True)
    def detect_outliers(self: HasData) -> dict[str, list[tuple]]:
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
