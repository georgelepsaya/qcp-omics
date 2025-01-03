import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from scipy.stats import boxcox
import numpy as np
from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar, Optional
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class PreprocessingMixin:
    @report_step(snapshot="combined", output=True)
    def split_train_test(self: T, method=None) -> pd.DataFrame:
        train_set, test_set = train_test_split(self.data, test_size=0.2, random_state=42)
        self.test_set = test_set
        self.data = train_set
        return test_set


    @report_step(snapshot="split")
    def split_numerical_categorical(self: T, method=None) -> None:
        self.data_numerical = self.data.select_dtypes(include=["float", "int"])
        self.data_categorical = self.data.select_dtypes(include=["category"])


    @report_step(snapshot="numerical")
    def scale_numerical_features(self: T, method="standard_scaler") -> None:
        if method == "standard_scaler":
            scaler = StandardScaler()
        elif method == "robust_scaler":
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unsupported scaling method: {method}")

        if len(self.data_numerical.columns) == 0:
            return

        self.data_numerical = pd.DataFrame(
            scaler.fit_transform(self.data_numerical),
            columns=self.data_numerical.columns,
            index=self.data_numerical.index,
        )


    @report_step(snapshot="numerical")
    def transform_numerical_features(self: T, method="box-cox") -> None:
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


    def _run_pca(self: T) -> Optional[dict]:

        if len(self.data_numerical.columns) == 0:
            return

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
    def dimensionality_reduction(self: T, method=None):
        result = self._run_pca()

        if result is None:
            return

        pca_data, per_var, cumulative_var = result.values()
        exp_variance_plot = self._explained_variance(cumulative_var)

        n_components = pca_data.shape[1]
        columns = [f"PC{i + 1}" for i in range(n_components)]

        df_pca = pd.DataFrame(
            data=pca_data,
            index=self.data.index,
            columns=columns
        )

        pca_plot = self._pca_plot(df_pca, per_var)

        return {
            "pca_data": df_pca,
            "explained_variance": exp_variance_plot,
            "pca_plot": pca_plot
        }
