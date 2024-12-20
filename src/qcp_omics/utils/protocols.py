from typing import Protocol
import pandas as pd

class HasData(Protocol):
    data: pd.DataFrame
    data_numeric: pd.DataFrame
    data_categorical: pd.DataFrame
    metadata: dict
