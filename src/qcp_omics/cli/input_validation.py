import os
import re
from typing import Any

from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

from qcp_omics.utils.utils import load_dataset


ALL_STEPS: list[dict[str, Any]] = [
    {"step": "identify_missing_values"},
    {"step": "handle_missing_values"},
    {"step": "handle_outliers", "methods": ["IQR", "zscore"]},
    {"step": "split_train_test"},
    {"step": "split_numerical_categorical"},
    {"step": "scale_numerical_features", "methods": ["standard_scaler", "robust_scaler"] },
    {"step": "transform_numerical_features", "methods": ["box-cox", "log2"]},
    {"step": "descriptive_statistics"},
    {"step": "pairwise_correlations_numerical", "methods": ["pearson", "spearman"]},
    {"step": "evaluate_distribution_features"},
    {"step": "dimensionality_reduction"},
]


class DatasetShapeWarning(Exception):
    def __init__(self, message: str, shape: tuple[int, int]) -> None:
        super().__init__(message)
        self.message = message
        self.shape = shape

    def __str__(self) -> str:
        return f"{self.message}: {self.shape[0]} rows, {self.shape[1]} columns."



class Input(BaseModel):
    dataset_type: str
    dataset_path: str
    metadata_path: str
    output_path: str
    report_path: str
    features_cols: bool
    en_header: bool
    is_raw: bool
    dtypes: dict[str, str]
    steps_to_run: list[dict[str, str]]


    # Extra boolean that allows the user to override the shape check if they confirm
    shape_override: bool = False


    @field_validator("dataset_type")
    @classmethod
    def check_dataset_type_value(cls, v: str) -> str:
        if v not in ["genomics", "proteomics", "clinical"]:
            raise ValueError("Incorrect dataset type value. Must be one of: genomics, proteomics, clinical.")
        return v


    @field_validator("dataset_path")
    @classmethod
    def check_dataset_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(f"Path '{v}' does not exist.")
        if not os.path.isfile(v):
            raise ValueError(f"Path '{v}' is not a file.")
        if not os.access(v, os.R_OK):
            raise ValueError(f"File '{v}' cannot be opened or read.")
        if os.path.getsize(v) == 0:
            raise ValueError(f"File '{v}' is empty.")
        _, ext = os.path.splitext(v)
        allowed_extensions = [".csv", ".tsv"]
        if ext.lower() not in allowed_extensions:
            raise ValueError(
                f"File '{v}' extension must be one of: {', '.join(allowed_extensions)}."
            )
        return v


    @field_validator("metadata_path")
    @classmethod
    def check_metadata_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(f"Metadata path '{v}' does not exist.")
        if not os.path.isfile(v):
            raise ValueError(f"Metadata path '{v}' is not a file.")
        if not os.access(v, os.R_OK):
            raise ValueError(f"Metadata file '{v}' cannot be opened or read.")
        if os.path.getsize(v) == 0:
            raise ValueError(f"Metadata file '{v}' is empty.")

        _, ext = os.path.splitext(v)
        if ext.lower() != ".json":
            raise ValueError(f"Metadata file '{v}' must have a .json extension.")
        return v

    @field_validator("output_path")
    @classmethod
    def check_output_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(f"Output path '{v}' does not exist.")
        if not os.path.isdir(v):
            raise ValueError(f"Output path '{v}' is not a directory.")
        if not os.access(v, os.W_OK):
            raise ValueError(f"Directory '{v}' is not writable.")
        return v


    @field_validator("report_path")
    @classmethod
    def check_report_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(f"Report path '{v}' does not exist.")
        if not os.path.isdir(v):
            raise ValueError(f"Report path '{v}' is not a directory.")
        if not os.access(v, os.W_OK):
            raise ValueError(f"Directory '{v}' is not writable.")
        return v


    @model_validator(mode="after")
    def validate_features_cols(self) -> Self:
        if not self.shape_override:
            df = load_dataset(self.dataset_path)
            nrows, ncols = df.shape
            if self.features_cols and nrows <= ncols:
                raise DatasetShapeWarning(
                    "Detected shape suggests features might be in rows instead of columns",
                    (nrows, ncols)
                )
            if not self.features_cols and nrows >= ncols:
                raise DatasetShapeWarning(
                    "Detected shape suggests features might be in columns instead of rows",
                    (nrows, ncols)
                )
        return self


    @model_validator(mode="after")
    def check_en_header(self) -> Self:
        if self.en_header:
            df = load_dataset(self.dataset_path)
            columns = df.columns.tolist()
            rows = df.index.tolist()

            pattern = re.compile(r"^[a-zA-Z0-9 ._\-]+$")

            invalid_columns = [col for col in columns if not pattern.match(str(col))]
            if invalid_columns:
                raise ValueError(f"Invalid column names detected (non-ASCII or unusual chars): {invalid_columns}")

            invalid_rows = [row for row in rows if not pattern.match(str(row))]
            if invalid_rows:
                raise ValueError(f"Invalid row index values detected (non-ASCII or unusual chars): {invalid_rows}")

        return self


    @model_validator(mode="after")
    def check_size(self) -> Self:
        df = load_dataset(self.dataset_path)
        if len(df.columns) < 1:
            raise ValueError("There can't be less than two columns in the dataset.")
        return self


    @model_validator(mode="after")
    def check_dtypes(self) -> Self:
        df = load_dataset(self.dataset_path)
        if not self.features_cols:
            df = df.T
        valid_dtypes = {"int", "float", "str", "object", "bool", "category"}

        for col_name, dtype_str in self.dtypes.items():
            if col_name not in df.columns:
                raise ValueError(f"dtypes error: column '{col_name}' not found in dataset.")
            if dtype_str not in valid_dtypes:
                raise ValueError(
                    f"dtypes error: invalid dtype '{dtype_str}' for column '{col_name}'. "
                    f"Must be one of: {', '.join(valid_dtypes)}."
                )

        return self


    @model_validator(mode="after")
    def check_steps_to_run(self) -> Self:
        step_index_map = {step_obj["step"]: i for i, step_obj in enumerate(ALL_STEPS)}

        # 1) Check that each step in steps_to_run is in ALL_STEPS in ascending index order
        last_index = -1
        for step_entry in self.steps_to_run:
            step_name = step_entry.get("step", "")
            if step_name not in step_index_map:
                raise ValueError(f"steps_to_run error: unknown step '{step_name}'.")

            current_index = step_index_map[step_name]
            if current_index <= last_index:
                raise ValueError(
                    f"steps_to_run error: step '{step_name}' is out of order. "
                    f"Must follow the original order in ALL_STEPS."
                )
            last_index = current_index

            # 2) If the step has 'methods' in ALL_STEPS, validate the chosen method
            all_steps_obj = ALL_STEPS[current_index]
            if "methods" in all_steps_obj:
                allowed_methods = all_steps_obj["methods"]
                user_method = step_entry.get("method")
                if isinstance(allowed_methods, list):
                    if user_method not in allowed_methods:
                        raise ValueError(
                            f"steps_to_run error: invalid method '{user_method}' "
                            f"for step '{step_name}'. Valid methods: {allowed_methods}"
                        )
                else:
                    raise ValueError(
                        f"steps_to_run error: internal config for step '{step_name}' has an invalid 'methods' format."
                    )

            # If the step has no 'methods' key in ALL_STEPS, but user provided one
            elif "method" in step_entry:
                raise ValueError(
                    f"steps_to_run error: step '{step_name}' does not support methods, "
                    f"but got method='{step_entry['method']}'."
                )

        # 3) If is_raw=False, require that steps_to_run contain *all* steps in correct order
        if self.is_raw is True:
            if len(self.steps_to_run) != len(ALL_STEPS):
                raise ValueError(
                    "steps_to_run error: is_raw=True requires that you run ALL steps, "
                    "but the steps_to_run list does not include every step."
                )


            official_steps = [s["step"] for s in ALL_STEPS]
            provided_steps = [s["step"] for s in self.steps_to_run]
            if official_steps != provided_steps:
                raise ValueError(
                    "steps_to_run error: is_raw=True requires the full pipeline in order. "
                    "The provided steps do not match exactly the official pipeline steps."
                )

        return self
