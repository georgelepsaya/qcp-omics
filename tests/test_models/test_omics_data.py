import pytest
import pandas as pd

from qcp_omics.models.omics_data import OmicsData

class DummyOmicsData(OmicsData):
    pass


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "GeneA": [1, 2, 3],
        "GeneB": [4, 5, 6]
    }, index=["S1", "S2", "S3"])


@pytest.fixture
def sample_metadata(tmp_path):
    return {
        "dataset_type": "genomics",
        "features_cols": True,
        "dtypes": {"GeneA": "int", "GeneB": "float"},
        "output_path": str(tmp_path),
        "steps_to_run": [
            {"step": "transpose"},
            {"step": "map_dtypes"},
        ]
    }


def test_omics_data_init(sample_data, sample_metadata):
    od = DummyOmicsData(sample_data, sample_metadata)
    assert od.data.equals(sample_data)
    assert od.metadata == sample_metadata
    assert "genomics" in repr(od)


def test_transpose(sample_data, sample_metadata):
    sample_metadata["features_cols"] = False
    od = DummyOmicsData(sample_data, sample_metadata)
    assert od.data.shape == (3, 2)
    od.transpose()
    assert od.data.shape == (2, 3)


def test_map_dtypes(sample_data, sample_metadata):
    od = DummyOmicsData(sample_data, sample_metadata)
    od.map_dtypes()
    assert str(od.data["GeneA"].dtype) == "int64"
    assert str(od.data["GeneB"].dtype) == "float64"


def test_execute_steps(sample_data, sample_metadata):
    sample_metadata["features_cols"] = False
    od = DummyOmicsData(sample_data, sample_metadata)
    od.execute_steps()
    assert od.data.shape == (2, 3)


@pytest.mark.parametrize("has_numerical,has_categorical,has_test", [
    (True, False, False),
    (False, True, True),
    (True, True, True),
])
def test_save_data_files(has_numerical, has_categorical, has_test, sample_data, sample_metadata, tmp_path):
    od = DummyOmicsData(sample_data, sample_metadata)
    od.data_numerical = pd.DataFrame() if not has_numerical else sample_data
    od.data_categorical = pd.DataFrame() if not has_categorical else sample_data.astype("category")
    od.test_set = pd.DataFrame() if not has_test else sample_data

    od.save_data_files()

    train_path = tmp_path / "train_data.csv"
    test_path = tmp_path / "test_data.csv"

    if has_numerical or has_categorical:
        assert train_path.exists() is True
    else:
        assert train_path.exists() is False

    if has_test:
        assert test_path.exists() is True
    else:
        assert test_path.exists() is False
