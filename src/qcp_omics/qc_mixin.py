from abc import abstractmethod
import pandas as pd
import typing as t
import json


class QCMixin:
    def map_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        with open('metadata.json', 'r') as f:
            mappings = json.load(f)
        dtype_mapping = mappings.get('dtypes', {})
        for col, dtype in dtype_mapping.items():
            if dtype == "category":
                df[col] = df[col].astype("category")
            elif dtype == "int":
                df[col] = df[col].astype("int")
            elif dtype == "float":
                df[col] = df[col].astype("float")
        return df

    def identify_missing_values(self, df: pd.DataFrame) -> dict[t.Any, float]:
        missing_values = df.isnull().mean() * 100
        missing = {col: pct for col, pct in missing_values.items() if pct > 0}
        return missing


