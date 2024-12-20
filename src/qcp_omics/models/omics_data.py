from abc import ABC
import pandas as pd
import json
import typing as t
from qcp_omics.report_generation.report_step import report_step


class OmicsData(ABC):
    def __init__(self, data: pd.DataFrame, metadata: dict) -> None:
        self.data = data
        self.data_numeric: t.Optional[pd.DataFrame] = None
        self.data_categorical: t.Optional[pd.DataFrame] = None
        self.metadata = metadata
        self.report_data: list[dict] = []


    def __repr__(self):
        return f"<OmicsData(dataset_type: {self.metadata['dataset_type']})>"


    def transpose(self) -> None:
        if not self.metadata["features_cols"]:
            print("Transposing the dataset")
            self.data = self.data.T


    def map_dtypes(self) -> None:
        print("Mapping the dtypes from metadata with the dataset")
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


    def split_numeric_categorical(self):
        self.data_numeric = self.data.select_dtypes(include=["float", "int"])
        self.data_categorical = self.data.select_dtypes(include=["category"])


    @report_step
    def step_omics(self):
        pass


    def execute_steps(self) -> None:
        steps = self.metadata["steps_to_run"]
        for step in steps:
            method = getattr(self, step, None)
            if callable(method):
                print(f"Executing step: {step}")
                method()
            else:
                print(f"Step {step} is not recognised an will be skipped.")
