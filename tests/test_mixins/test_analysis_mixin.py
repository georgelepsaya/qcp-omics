import pytest
import pandas as pd
from qcp_omics.models.clinical_data import ClinicalData


metadata_base = {
    "dtypes": {"X": "int", "Y": "int", "Z": "int"},
    "steps_to_run": [{"step": "identify_missing_values"}]
}


class DummyAnalysis(ClinicalData):
    def __init__(self, data: pd.DataFrame, metadata: dict):
        super().__init__(data, metadata)


@pytest.fixture
def numerical_data():
    return pd.DataFrame({
        "X": [1, 2, 3, 4],
        "Y": [2, 4, 6, 8],
        "Z": [10, 15, 5, 20],
    }, index=["s1", "s2", "s3", "s4"])


def test_descriptive_statistics(numerical_data):
    dummy = DummyAnalysis(numerical_data, metadata_base)
    dummy.split_numerical_categorical()
    stats = dummy.descriptive_statistics()
    assert "mean" in stats.columns
    assert "kurtosis" in stats.columns
    assert stats.loc["X", "mean"] == pytest.approx(2.5)


def test_pairwise_correlations_numerical(numerical_data):
    dummy = DummyAnalysis(numerical_data, metadata_base)
    dummy.split_numerical_categorical()
    result = dummy.pairwise_correlations_numerical(method="pearson")
    corr_matrix = result["corr_matrix"]
    assert corr_matrix.shape == (3, 3)
    assert "heatmap" in result


def test_evaluate_distribution_features(numerical_data):
    dummy = DummyAnalysis(numerical_data, metadata_base)
    dummy.split_numerical_categorical()
    result = dummy.evaluate_distribution_features()
    assert "hist_plots" in result
    assert "<div>" in result["hist_plots"]
