import pytest
import pandas as pd
from click import UsageError
from qcp_omics.utils.utils import load_dataset, handle_json_input


def test_load_dataset_csv(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("ID,Value\nA,1\nB,2\n", encoding="utf-8")

    df = load_dataset(str(csv_file))
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 1)
    assert list(df.index) == ["A", "B"]
    assert list(df.columns) == ["Value"]


def test_load_dataset_tsv(tmp_path):
    tsv_file = tmp_path / "data.tsv"
    tsv_file.write_text("ID\tValue\nA\t3\nB\t4\n", encoding="utf-8")

    df = load_dataset(str(tsv_file))
    assert df.shape == (2, 1)
    assert df.loc["A", "Value"] == 3


def test_load_dataset_unsupported_ext(tmp_path):
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("some text", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        load_dataset(str(txt_file))


def test_handle_json_input_valid(tmp_path):
    json_file = tmp_path / "metadata.json"
    json_content = {"someKey": "someValue"}
    json_file.write_text('{"someKey": "someValue"}', encoding="utf-8")

    result = handle_json_input(str(json_file))
    assert result == json_content


def test_handle_json_input_non_json(tmp_path):
    fake_file = tmp_path / "input.txt"
    fake_file.write_text("not really json", encoding="utf-8")
    with pytest.raises(UsageError, match="must be a JSON file"):
        handle_json_input(str(fake_file))


def test_handle_json_input_invalid_json(tmp_path):
    bad_json = tmp_path / "metadata.json"
    bad_json.write_text("{Invalid JSON here", encoding="utf-8")
    with pytest.raises(UsageError, match="Could not open file"):
        handle_json_input(str(bad_json))
