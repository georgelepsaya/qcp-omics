from abc import ABC
from typing import Optional
import pandas as pd

class OmicsData(ABC):
    def __init__(self, data: pd.DataFrame, metadata: dict) -> None:
        self.data = data
        self.data_numerical: Optional[pd.DataFrame] = None
        self.data_categorical: Optional[pd.DataFrame] = None
        self.test_set: Optional[pd.DataFrame] = None
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
        dtype_mapping = self.metadata["dtypes"]
        for col, dtype in dtype_mapping.items():
            if col in self.data.columns:
                if dtype == "category":
                    self.data[col] = self.data[col].astype("category")
                elif dtype == "int":
                    self.data[col] = self.data[col].astype("int")
                elif dtype == "float":
                    self.data[col] = self.data[col].astype("float")


    # def split_numeric_categorical(self):
    #     self.data_numeric = self.data.select_dtypes(include=["float", "int"])
    #     self.data_categorical = self.data.select_dtypes(include=["category"])


    @staticmethod
    def _visualize_data_snapshot(df: pd.DataFrame) -> str:
        html_table = df.to_html(classes="table table-striped table-bordered table-hover")
        return html_table


    def execute_steps(self) -> None:
        steps = self.metadata["steps_to_run"]
        for step in steps:
            step_impl = getattr(self, step["step"], None)
            method = step.get("method", None)
            if callable(step_impl):
                if method:
                    print(f"Executing step {step['step']} with {step['method']} method...")
                else:
                    print(f"Executing step {step['step']}...")
                step_impl(method=method)
            else:
                print(f"Step {step['step']} is not recognised and will be skipped.")
