from abc import ABC
import pandas as pd
import json


class OmicsData(ABC):
    def __init__(self, data: pd.DataFrame, metadata: dict) -> None:
        self.data = data
        self.metadata = metadata

    def __repr__(self):
        return f"<OmicsData(dataset_type: {self.metadata['dataset_type']})>"

    def map_dtypes(self):
        metadata_path = self.metadata["metadata_path"]
        with open(metadata_path, "r") as f:
            mappings = json.load(f)
        dtype_mapping = mappings.get("dtypes", {})
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

