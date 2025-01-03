from pydantic import BaseModel, field_validator, model_validator
import os
from typing_extensions import Self
import re
from qcp_omics.utils.utils import load_dataset


class DatasetShapeWarning(Exception):
    def __init__(self, message: str, value: tuple[int, int]) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}: {self.value[0]} rows, {self.value[1]} columns."


class Input(BaseModel):
    dataset_type: str
    dataset_path: str
    metadata_path: str
    output_path: str
    report_path: str
    features_cols: bool
    en_header: bool
    all_numerical: bool
    is_raw: bool
    dtypes: dict[str, str]
    steps_to_run: list[dict[str, str]]


    # TODO: validate metadata path
    # TODO: validate that metadata is a valid json file with dtypes (required)
    # TODO: validate metadata dtypes have all features
    # TODO: validate target feature


    @field_validator("dataset_type")
    @classmethod
    def check_dataset_type_value(cls, v: str) -> str:
        if v not in ["genomics", "proteomics", "clinical"]:
            raise ValueError("Incorrect dataset type value")
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
            raise ValueError(f"File '{v}' extension is not one of: {', '.join(allowed_extensions)}.")
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


    @model_validator(mode="after")
    def check_features_cols(self) -> Self:
        df = load_dataset(self.dataset_path)
        shape = df.shape
        # check for contradiction with specified shape
        if self.features_cols and shape[0] <= shape[1]:
            raise DatasetShapeWarning("Features may be in rows instead of columns due to detected shape", shape)
        elif not self.features_cols and shape[0] >= shape[1]:
            raise DatasetShapeWarning("Features may be in columns instead of rows due to detected shape", shape)
        return self


    @model_validator(mode="after")
    def check_en_header(self) -> Self:
        df = load_dataset(self.dataset_path)
        columns = df.columns.to_list()
        rows = df.index.to_list()
        pattern = re.compile(r"^[a-zA-Z0-9 ._\-]+$")
        if self.en_header:
            invalid_columns = [col for col in columns if not pattern.match(col)]
            if invalid_columns:
                raise ValueError(f"Invalid column names detected: {invalid_columns}")
            invalid_rows = [row for row in rows if not pattern.match(row)]
            if invalid_rows:
                raise ValueError(f"Invalid row index values detected: {invalid_rows}")
        return self
