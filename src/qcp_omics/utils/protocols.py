from typing import Protocol, TypedDict, Optional
import pandas as pd

class HasData(Protocol):
    """
    Protocol for objects that contain datasets and metadata.

    Attributes:
        data (pd.DataFrame): The main dataset.
        data_numerical (pd.DataFrame): Subset of the dataset containing only numerical features.
        data_categorical (pd.DataFrame): Subset of the dataset containing only categorical features.
        test_set (pd.DataFrame): Test split of the data.
        metadata (dict): Dictionary containing metadata about the dataset.
        report_data (list[dict]): List of dictionaries containing report-related data.
    """
    data: pd.DataFrame
    data_numerical: pd.DataFrame
    data_categorical: pd.DataFrame
    test_set: pd.DataFrame
    metadata: dict
    report_data: list[dict]
