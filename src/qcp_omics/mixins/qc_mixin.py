import numpy as np
import pandas as pd
from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar, Any, Tuple
from qcp_omics.utils.protocols import HasData
from sklearn.impute import SimpleImputer


T = TypeVar("T", bound=HasData)


class QCMixin:
    @staticmethod
    def _identify_missing_values(df: pd.DataFrame) -> dict[Any, float]:
        missing_values = df.isnull().mean() * 100
        filtered_missing = {col: pct for col, pct in missing_values.items() if pct > 0}
        sorted_missing = dict(sorted(filtered_missing.items(), key=lambda item: item[1], reverse=True))
        return sorted_missing


    def _impute_mean(self: T) -> None:
        imputer = SimpleImputer(strategy="mean")
        self.data_numeric[:] = imputer.fit_transform(self.data_numeric)


    def _impute_mode(self: T) -> None:
        imputer = SimpleImputer(strategy="most_frequent")
        self.data_categorical[:] = imputer.fit_transform(self.data_categorical)


    @staticmethod
    def _detect_outliers_iqr(df: pd.DataFrame) -> dict[str, list[tuple]]:
        outliers = {}
        for col in df.columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            col_outliers = df[col][outliers_mask]
            if not col_outliers.empty:
                outliers[col] = list(col_outliers.items())
        return outliers


    @staticmethod
    def _detect_outliers_zscore(df: pd.DataFrame, threshold: float = 3.0) -> dict[str, list[tuple]]:
        outliers = {}
        for col in df.columns:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers_mask = z_scores > threshold
            col_outliers = df[col][outliers_mask]
            if not col_outliers.empty:
                outliers[col] = list(col_outliers.items())
        return outliers


    def _detect_outliers(self: T, method="iqr") -> dict[str, list[tuple]]:
        if method == "zscore":
            outliers = self._detect_outliers_zscore(self.data_numeric)
        else:
            outliers = self._detect_outliers_iqr(self.data_numeric)
        return outliers


    @report_step(output=True)
    def identify_missing_values(self: T, method=None) -> dict[Any, float]:
        return self._identify_missing_values(self.data_numeric) | self._identify_missing_values(self.data_categorical)


    @report_step(snapshot=True)
    def handle_missing_values(self: T, method="impute_mean"):
        miss_cols_num = self._identify_missing_values(self.data_numeric)
        miss_cols_cat = self._identify_missing_values(self.data_categorical)
        for col, miss in miss_cols_num.items():
            if miss >= 30:
                self.data.drop(col, axis=1, inplace=True)
                self.data_numeric.drop(col, axis=1, inplace=True)
        for col, miss in miss_cols_cat.items():
            if miss >= 30:
                self.data.drop(col, axis=1, inplace=True)
                self.data_categorical.drop(col, axis=1, inplace=True)
        self._impute_mode()
        if method == "impute_mean":
            self._impute_mean()


    @report_step(snapshot=True, output=True)
    def handle_outliers(self: T, method="iqr") -> dict[str, list[tuple]]:
        outliers = self._detect_outliers(method=method)
        for col, outliers_list in outliers.items():
            median_value = self.data_numeric[col].median()
            for index, _ in outliers_list:
                self.data_numeric.at[index, col] = median_value
        return outliers
