import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler
from scipy.stats import boxcox
import numpy as np
from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar
from qcp_omics.utils.protocols import HasData


T = TypeVar("T", bound=HasData)


class PreprocessingMixin:
    @report_step(snapshot=True)
    def scale_features(self: T, method="standard_scaler") -> None:
        if method == "standard_scaler":
            scaler = StandardScaler()
        elif method == "robust_scaler":
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unsupported scaling method: {method}")

        self.data_numeric = pd.DataFrame(
            scaler.fit_transform(self.data_numeric),
            columns=self.data_numeric.columns,
            index=self.data_numeric.index,
        )


    @report_step(snapshot=True)
    def transform(self: T, method="box-cox") -> None:
        min_val = self.data_numeric.min().min()
        if min_val <= 0:
            shift = abs(min_val) + 1
            self.data_numeric += shift

        if method == "box-cox":
            self.data_numeric = pd.DataFrame(
                self.data_numeric.apply(lambda col: boxcox(col)[0] if col.var() > 0 else col),
                columns=self.data_numeric.columns,
                index=self.data_numeric.index,
            )
        elif method == "log2":
            self.data_numeric = self.data_numeric.apply(
                lambda col: np.log2(col) if col.var() > 0 else col
            )
        else:
            raise ValueError(f"Unsupported transformation method: {method}")


    @report_step()
    def dimensionality_reduction(self: T, method="PCA"):
        pass

