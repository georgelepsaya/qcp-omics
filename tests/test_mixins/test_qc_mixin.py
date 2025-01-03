import pytest
import pandas as pd
from qcp_omics.models.clinical_data import ClinicalData


metadata_base = {
    "dtypes": {"A": "int", "B": "int", "C": "int"}
}


class DummyQC(ClinicalData):
    def __init__(self, data: pd.DataFrame, metadata: dict):
        super().__init__(data, metadata)


@pytest.fixture
def df_with_missing_and_outliers():
    return pd.DataFrame({
        "A": [1, 2, None, 100, 2],
        "B": [5, 6, 7, 8, None],
        "C": [1, 1, 1, 1, 1]
    }, index=["s1", "s2", "s3", "s4", "s5"])


def test_identify_missing_values(df_with_missing_and_outliers):
    dummy = DummyQC(df_with_missing_and_outliers, metadata_base)
    missing_vals = dummy.identify_missing_values()
    assert "A" in missing_vals
    assert missing_vals["A"] > 0
    assert "B" in missing_vals
    assert missing_vals["B"] > 0


def test_handle_missing_values(df_with_missing_and_outliers):
    dummy = DummyQC(df_with_missing_and_outliers, metadata_base)
    dummy.handle_missing_values()
    assert dummy.data.isnull().sum().sum() == 0


def test_handle_outliers(df_with_missing_and_outliers):
    dummy = DummyQC(df_with_missing_and_outliers, metadata_base)
    result = dummy.handle_outliers(method="iqr")

    outliers_dict = result["outliers"]
    assert "A" in outliers_dict
    assert 100 not in dummy.data["A"].values

    assert "boxplots" in result
    assert "html" in result["boxplots"]
