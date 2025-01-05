import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from scipy.stats import boxcox
import numpy as np
from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar, Optional, Dict
from qcp_omics.utils.protocols import HasData

T = TypeVar("T", bound=HasData)

class PreprocessingMixin:
    """
    A mixin class for preprocessing data, including splitting datasets, scaling,
    transforming features, and applying dimensionality reduction techniques.
    """

    @report_step(snapshot="combined", output=True)
    def split_train_test(self: T) -> pd.DataFrame:
        """
        Split the dataset into training and testing sets.

        Returns:
            pd.DataFrame: The test set.
        """
        train_set, test_set = train_test_split(self.data, test_size=0.2, random_state=42)
        self.test_set = test_set
        self.data = train_set
        return test_set

    @report_step(snapshot="split")
    def split_numerical_categorical(self: T) -> None:
        """
        Split the dataset into numerical and categorical subsets.
        """
        self.data_numerical = self.data.select_dtypes(include=["float", "int"])
        self.data_categorical = self.data.select_dtypes(include=["category"])

    @report_step(snapshot="numerical")
    def scale_numerical_features(self: T, method: str = "standard_scaler") -> None:
        """
        Scale numerical features using the specified scaling method.

        Args:
            method (str): The scaling method to use ("standard_scaler" or "robust_scaler").
        """
        scaler = StandardScaler() if method == "standard_scaler" else RobustScaler()

        if self.data_numerical.empty:
            return

        self.data_numerical = pd.DataFrame(
            scaler.fit_transform(self.data_numerical),
            columns=self.data_numerical.columns,
            index=self.data_numerical.index,
        )

    @report_step(snapshot="numerical")
    def transform_numerical_features(self: T, method: str = "box-cox") -> None:
        """
        Transform numerical features using the specified method.

        Args:
            method (str): The transformation method to use ("box-cox" or "log2").

        Raises:
            ValueError: If the transformation method is unsupported.
        """
        min_val = self.data_numerical.min().min()
        if min_val <= 0:
            shift = abs(min_val) + 1
            self.data_numerical += shift

        if method == "box-cox":
            self.data_numerical = pd.DataFrame(
                self.data_numerical.apply(lambda col: boxcox(col)[0] if col.var() > 0 else col),
                columns=self.data_numerical.columns,
                index=self.data_numerical.index,
            )
        elif method == "log2":
            self.data_numerical = self.data_numerical.apply(
                lambda col: np.log2(col) if col.var() > 0 else col
            )
        else:
            raise ValueError(f"Unsupported transformation method: {method}")

    def _run_pca(self: T) -> Optional[Dict[str, np.ndarray]]:
        """
        Perform Principal Component Analysis (PCA) on numerical features.

        Returns:
            Optional[Dict[str, np.ndarray]]: A dictionary containing PCA results and explained variance metrics,
            or None if there are no numerical features.
        """
        if self.data_numerical.empty:
            return None

        pca = PCA()
        pca.fit(self.data_numerical)
        pca_data = pca.transform(self.data_numerical)

        per_var = np.round(pca.explained_variance_ratio_ * 100, decimals=1)
        cumulative_var = np.cumsum(pca.explained_variance_ratio_) * 100

        return {
            "pca_data": pca_data,
            "per_var": per_var,
            "cumulative_var": cumulative_var
        }

    @report_step(output=True)
    def dimensionality_reduction(self: T) -> Optional[Dict[str, any]]:
        """
        Apply dimensionality reduction using PCA and generate relevant visualizations.

        Returns:
            Optional[Dict[str, any]]: A dictionary containing PCA data, explained variance plot, and PCA plot.
        """
        result = self._run_pca()

        if result is None:
            return None

        pca_data, per_var, cumulative_var = result.values()
        exp_variance_plot = self._explained_variance(cumulative_var) if hasattr(self, '_explained_variance') else None

        n_components = pca_data.shape[1]
        columns = [f"PC{i + 1}" for i in range(n_components)]

        df_pca = pd.DataFrame(
            data=pca_data,
            index=self.data.index,
            columns=columns
        )

        pca_plot = self._pca_plot(df_pca, per_var) if hasattr(self, '_pca_plot') else None

        return {
            "pca_data": df_pca,
            "explained_variance": exp_variance_plot,
            "pca_plot": pca_plot
        }
