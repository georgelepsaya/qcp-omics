from typing import Protocol, TypedDict, Optional
import pandas as pd

class HasData(Protocol):
    data: pd.DataFrame
    data_numerical: pd.DataFrame
    data_categorical: pd.DataFrame
    test_set: pd.DataFrame
    metadata: dict
    report_data: list[dict]
