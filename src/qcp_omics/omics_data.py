from abc import ABC
import pandas as pd
import json


class OmicsData(ABC):
    def __init__(self, data: pd.DataFrame, metadata: dict) -> None:
        self.data = data
        self.metadata = metadata

    def map_dtypes(self):
        metadata_path = self.metadata["metadata_path"]
        with open(metadata_path, "r") as f:
            mappings = json.load(f)
        dtype_mapping = mappings.get('dtypes', {})
        for col, dtype in dtype_mapping.items():
            if col in self.data.columns:
                if dtype == "category":
                    self.data[col] = self.data[col].astype("category")
                elif dtype == "int":
                    self.data[col] = self.data[col].astype("int")
                elif dtype == "float":
                    self.data[col] = self.data[col].astype("float")

    def split_numeric_categorical(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        numeric = self.data.select_dtypes(include=["float", "int"])
        categorical = self.data.select_dtypes(include=["category"])
        return numeric, categorical

    @staticmethod
    def detect_outliers(df: pd.DataFrame):
        outliers = {}
        for col in df.columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            col_outliers = df[col][(df[col] < lower_bound) | (df[col] > upper_bound)]
            if not col_outliers.empty:
                outliers[col] = list(col_outliers.items())
        return outliers

    def execute_steps(self) -> None:
        steps: list[str] = self.metadata["steps"]
        self.map_dtypes()
        data_numeric, data_categorical = self.split_numeric_categorical()
        for step in steps:
            match step:
                case "identify_missing_values":
                    pass
                case "detect_outliers":
                    self.detect_outliers(data_numeric)
                case "handle_missing_values":
                    pass
                case "handle_outliers":
                    pass
                case "normalize_numerical_features":
                    pass
                case "transform":
                    pass
                case "encode_categorical_variables":
                    pass
                case "scale_features":
                    pass
                case "dimensionality_reduction":
                    pass
                case "distribution_numerical":
                    pass
                case "distribution_categorical":
                    pass
                case "visualize_outliers":
                    pass
                case "correlation_heatmaps":
                    pass
                case "correlation_heatmaps":
                    pass
                case "feature_interdependencies":
                    pass
                case "categorical_feature_relationships":
                    pass
                case "visualize_dimensionality_reduction":
                    pass
                case "descriptive_statistics":
                    pass
                case "group_comparisons":
                    pass
                case "correlation_coefficients":
                    pass
                case "multicollinearity":
                    pass
                case "build_models":
                    pass
                case "evaluate_model_performance":
                    pass
                case "feature_importance_analysis":
                    pass
                case "hypothesis_testing":
                    pass


