import numpy as np
import pandas as pd
from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar, Any, Dict, List, Tuple
from qcp_omics.utils.protocols import HasData
from sklearn.impute import SimpleImputer

T = TypeVar("T", bound=HasData)

class QCMixin:
    """
    A mixin class providing methods for quality control operations on a dataset.
    Includes functionality for handling missing values, imputing data, and detecting outliers.
    """

    @staticmethod
    def _identify_missing_values(df: pd.DataFrame) -> Dict[str, float]:
        """
        Identify columns with missing values and calculate the percentage of missing data.

        Args:
            df (pd.DataFrame): The DataFrame to analyze.

        Returns:
            Dict[str, float]: A dictionary of column names and their respective missing value percentages.
        """
        missing_values = df.isnull().mean() * 100
        filtered_missing = {col: pct for col, pct in missing_values.items() if pct > 0}
        return dict(sorted(filtered_missing.items(), key=lambda item: item[1], reverse=True))

    def _impute_mean(self: T) -> None:
        """
        Impute missing values in numerical columns with the mean.
        """
        imputer = SimpleImputer(strategy="mean")
        data_numerical = self.data.select_dtypes(include=["float", "int"])
        if data_numerical.empty:
            return

        imputed_values = imputer.fit_transform(data_numerical)
        imputed_df = pd.DataFrame(imputed_values, columns=data_numerical.columns, index=data_numerical.index)
        self.data[data_numerical.columns] = imputed_df.astype(data_numerical.dtypes)

    def _impute_mode(self: T) -> None:
        """
        Impute missing values in categorical columns with the most frequent value (mode).
        """
        imputer = SimpleImputer(strategy="most_frequent")
        data_categorical = self.data.select_dtypes(include=["category"])
        if data_categorical.empty:
            return

        imputed_values = imputer.fit_transform(data_categorical)
        imputed_df = pd.DataFrame(imputed_values, columns=data_categorical.columns, index=data_categorical.index)
        self.data[data_categorical.columns] = imputed_df.astype('category')

    @staticmethod
    def _detect_outliers_iqr(df: pd.DataFrame) -> Dict[str, List[Tuple[int, Any]]]:
        """
        Detect outliers in numerical columns using the Interquartile Range (IQR) method.

        Args:
            df (pd.DataFrame): The DataFrame containing numerical data.

        Returns:
            Dict[str, List[Tuple[int, Any]]]: A dictionary where keys are column names and values are lists of tuples,
            each tuple containing the index and outlier value.
        """
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
    def _detect_outliers_zscore(df: pd.DataFrame, threshold: float = 3.0) -> Dict[str, List[Tuple[int, Any]]]:
        """
        Detect outliers in numerical columns using the Z-score method.

        Args:
            df (pd.DataFrame): The DataFrame containing numerical data.
            threshold (float): The Z-score threshold for defining outliers. Defaults to 3.0.

        Returns:
            Dict[str, List[Tuple[int, Any]]]: A dictionary where keys are column names and values are lists of tuples,
            each tuple containing the index and outlier value.
        """
        outliers = {}
        for col in df.columns:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers_mask = z_scores > threshold
            col_outliers = df[col][outliers_mask]
            if not col_outliers.empty:
                outliers[col] = list(col_outliers.items())
        return outliers

    def _detect_outliers(self: T, df: pd.DataFrame, method: str = "iqr") -> Dict[str, List[Tuple[int, Any]]]:
        """
        Detect outliers in a DataFrame using the specified method (IQR or Z-score).

        Args:
            df (pd.DataFrame): The DataFrame containing numerical data.
            method (str): The method for detecting outliers ("iqr" or "zscore"). Defaults to "iqr".

        Returns:
            Dict[str, List[Tuple[int, Any]]]: A dictionary of outliers detected in the data.
        """
        if method == "zscore":
            return self._detect_outliers_zscore(df)
        return self._detect_outliers_iqr(df)

    @report_step(output=True)
    def identify_missing_values(self: T) -> Dict[str, float]:
        """
        Identify missing values in the dataset and return their percentages.

        Returns:
            Dict[str, float]: A dictionary of columns and their missing value percentages.
        """
        return self._identify_missing_values(self.data)

    @report_step(snapshot="combined")
    def handle_missing_values(self: T) -> None:
        """
        Handle missing values by dropping columns with more than 30% missing data,
        imputing categorical data with mode, and imputing numerical data with mean.
        """
        missing_columns = self._identify_missing_values(self.data)
        if not missing_columns:
            return

        # Drop columns with >= 30% missing data
        for col, missing_percentage in missing_columns.items():
            if missing_percentage >= 30:
                self.data.drop(columns=[col], inplace=True)

        self._impute_mode()
        self._impute_mean()

    @report_step(snapshot="combined", output=True)
    def handle_outliers(self: T, method: str = "iqr") -> Dict[str, Any]:
        """
        Handle outliers in the dataset by replacing them with the column's median value.

        Args:
            method (str): The method for detecting outliers ("iqr" or "zscore"). Defaults to "iqr".

        Returns:
            Dict[str, Any]: A dictionary containing outlier information and optional visualizations.
        """
        data_numerical = self.data.select_dtypes(include=["float", "int"])
        if data_numerical.empty:
            return {"outliers": {}, "boxplots": []}

        outliers = self._detect_outliers(data_numerical, method=method)

        # Replace outliers with median value
        for col, outliers_list in outliers.items():
            median_value = self.data[col].median()
            for index, _ in outliers_list:
                self.data.at[index, col] = median_value

        # Generate boxplots for visualization (if implemented)
        boxplots = self._box_plots(data_numerical, list(outliers.keys()))

        return {
            "outliers": outliers,
            "boxplots": boxplots
        }
