import pytest
import pandas as pd
from qcp_omics.models.clinical_data import ClinicalData


metadata_base = {
    "dtypes": {"Num1": "int", "Num2": "int", "Cat1": "category"},
    "steps_to_run": [{"step": "identify_missing_values"}]
}


class DummyPreprocessing(ClinicalData):
    def __init__(self, data: pd.DataFrame, metadata: dict):
        super().__init__(data, metadata)


@pytest.fixture
def small_dataset():
    # Some numeric and categorical data
    df = pd.DataFrame({
        "Num1": [1, 2, 3, 4, 5],
        "Num2": [10, 20, 30, 40, 50],
        "Cat1": pd.Series(["A", "B", "A", "B", "C"],
                          index=["s1", "s2", "s3", "s4", "s5"],
                          dtype="category")
    }, index=["s1", "s2", "s3", "s4", "s5"])
    return df


def test_split_train_test(small_dataset):
    dummy = DummyPreprocessing(small_dataset, metadata_base)
    test_set = dummy.split_train_test()
    assert test_set.shape[0] == 1
    assert dummy.data.shape[0] == 4


def test_split_numerical_categorical(small_dataset):
    dummy = DummyPreprocessing(small_dataset, metadata_base)
    dummy.split_train_test()
    dummy.split_numerical_categorical()
    assert list(dummy.data_numerical.columns) == ["Num1", "Num2"]
    assert list(dummy.data_categorical.columns) == ["Cat1"]


def test_scale_numerical_features(small_dataset):
    dummy = DummyPreprocessing(small_dataset, metadata_base)
    dummy.split_train_test()
    dummy.split_numerical_categorical()
    dummy.scale_numerical_features(method="standard_scaler")
    df_scaled = dummy.data_numerical
    assert abs(df_scaled["Num1"].mean()) < 1e-7
    assert abs(df_scaled["Num2"].mean()) < 1e-7


def test_transform_numerical_features_boxcox(small_dataset):
    dummy = DummyPreprocessing(small_dataset, metadata_base)
    dummy.split_train_test()
    dummy.split_numerical_categorical()
    dummy.scale_numerical_features(method="standard_scaler")
    dummy.transform_numerical_features(method="box-cox")
    assert (dummy.data_numerical < 0).sum().sum() == 0


def test_transform_numerical_features_log2(small_dataset):
    dummy = DummyPreprocessing(small_dataset, metadata_base)
    dummy.split_train_test()
    dummy.split_numerical_categorical()
    dummy.transform_numerical_features(method="log2")
    assert not dummy.data_numerical.isnull().values.any()


def test_dimensionality_reduction(small_dataset):
    dummy = DummyPreprocessing(small_dataset, metadata_base)
    dummy.split_train_test()
    dummy.split_numerical_categorical()
    result = dummy.dimensionality_reduction()
    assert "pca_data" in result
    assert "pca_plot" in result
