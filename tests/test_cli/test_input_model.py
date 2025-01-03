import os
import pytest
from pydantic import ValidationError

from qcp_omics.cli.input_validation import Input, DatasetShapeWarning, ALL_STEPS
from qcp_omics.utils.utils import load_dataset


# FIXTURES

@pytest.fixture
def tmp_csv_file(tmp_path) -> str:
    csv_path = tmp_path / "test_dataset.csv"
    csv_path.write_text("id,col1,col2\nsmpl1,v1,v2\nsmpl2,v3,v4\nsmpl3,v5,v6\n", encoding="utf-8")
    return str(csv_path)


@pytest.fixture
def tmp_tsv_file(tmp_path) -> str:
    tsv_path = tmp_path / "test_dataset.tsv"
    tsv_path.write_text("id,col1,col2\nsmpl1,v1,v2\nsmpl2,v3,v4\nsmpl3,v5,v6\n", encoding="utf-8")
    return str(tsv_path)


@pytest.fixture
def tmp_json_file(tmp_path) -> str:
    json_path = tmp_path / "test_metadata.json"
    json_path.write_text("{}", encoding="utf-8")
    return str(json_path)


@pytest.fixture
def writable_dir(tmp_path) -> str:
    return str(tmp_path)


@pytest.fixture
def minimal_valid_input(tmp_csv_file, tmp_json_file, writable_dir):
    return {
        "dataset_type": "genomics",
        "dataset_path": tmp_csv_file,
        "metadata_path": tmp_json_file,
        "output_path": writable_dir,
        "report_path": writable_dir,
        "features_cols": True,
        "en_header": True,
        "is_raw": True,
        "dtypes": {"col1":"str","col2":"str"},
        "steps_to_run": [
            {"step": step["step"]} if "methods" not in step
            else {"step": step["step"], "method": step["methods"][0]}
            for step in ALL_STEPS
        ],
    }


# TESTS FOR VALID INPUT (HAPPY PATH)

def test_valid_input_success(minimal_valid_input):
    model = Input(**minimal_valid_input)
    assert model.dataset_type == "genomics"
    assert model.is_raw is True
    assert len(model.steps_to_run) == len(ALL_STEPS)
    df = load_dataset(model.dataset_path)
    assert not df.empty


# TESTS FOR DATASET_TYPE

def test_dataset_type_invalid(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_type"] = "invalid_type"
    with pytest.raises(ValidationError, match="Incorrect dataset type value"):
        Input(**bad_input)


# TESTS FOR DATASET_PATH

def test_dataset_path_does_not_exist(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = "/does/not/exist.csv"
    with pytest.raises(ValidationError, match="does not exist"):
        Input(**bad_input)


def test_dataset_path_is_directory(minimal_valid_input, tmp_path):
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(tmp_path)  # a directory, not a file
    with pytest.raises(ValidationError, match="is not a file"):
        Input(**bad_input)


def test_dataset_path_unreadable(minimal_valid_input, tmp_path):
    # Make a file, but remove read permission
    file_path = tmp_path / "unreadable.csv"
    file_path.write_text("content")
    os.chmod(file_path, 0o200)  # write-only
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(file_path)
    with pytest.raises(ValidationError, match="cannot be opened or read"):
        Input(**bad_input)


def test_dataset_path_empty(minimal_valid_input, tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.touch()  # create empty file
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(file_path)
    with pytest.raises(ValidationError, match="File '.*' is empty"):
        Input(**bad_input)


def test_dataset_path_wrong_extension(minimal_valid_input, tmp_path):
    file_path = tmp_path / "myfile.txt"
    file_path.write_text("something", encoding="utf-8")
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(file_path)
    with pytest.raises(ValidationError, match="extension must be one of"):
        Input(**bad_input)


# TESTS FOR METADATA_PATH

def test_metadata_path_does_not_exist(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["metadata_path"] = "/this/metadata/does/not/exist.json"
    with pytest.raises(ValidationError, match="does not exist"):
        Input(**bad_input)


def test_metadata_path_is_directory(minimal_valid_input, tmp_path):
    bad_input = minimal_valid_input.copy()
    bad_input["metadata_path"] = str(tmp_path)  # directory
    with pytest.raises(ValidationError, match="is not a file"):
        Input(**bad_input)


def test_metadata_path_unreadable(minimal_valid_input, tmp_path):
    json_file = tmp_path / "meta.json"
    json_file.write_text("{}", encoding="utf-8")
    os.chmod(json_file, 0o200)  # write-only
    bad_input = minimal_valid_input.copy()
    bad_input["metadata_path"] = str(json_file)
    with pytest.raises(ValidationError, match="cannot be opened or read"):
        Input(**bad_input)


def test_metadata_path_empty(minimal_valid_input, tmp_path):
    json_file = tmp_path / "meta.json"
    json_file.touch()  # zero bytes
    bad_input = minimal_valid_input.copy()
    bad_input["metadata_path"] = str(json_file)
    with pytest.raises(ValidationError, match="file '.*' is empty"):
        Input(**bad_input)


def test_metadata_path_wrong_extension(minimal_valid_input, tmp_path):
    json_file = tmp_path / "invalid_metadata.txt"
    json_file.write_text("{}", encoding="utf-8")
    bad_input = minimal_valid_input.copy()
    bad_input["metadata_path"] = str(json_file)
    with pytest.raises(ValidationError, match="must have a .json extension"):
        Input(**bad_input)


# TESTS FOR OUTPUT_PATH

def test_output_path_does_not_exist(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["output_path"] = "/non/existent/directory"
    with pytest.raises(ValidationError, match="does not exist"):
        Input(**bad_input)


def test_output_path_is_file(minimal_valid_input, tmp_csv_file):
    bad_input = minimal_valid_input.copy()
    bad_input["output_path"] = tmp_csv_file  # a file, not directory
    with pytest.raises(ValidationError, match="is not a directory"):
        Input(**bad_input)


def test_output_path_not_writable(minimal_valid_input, tmp_path):
    # Make a directory read-only
    ro_dir = tmp_path / "ro_dir"
    ro_dir.mkdir()
    os.chmod(ro_dir, 0o500)  # read + execute, no write
    bad_input = minimal_valid_input.copy()
    bad_input["output_path"] = str(ro_dir)
    with pytest.raises(ValidationError, match="is not writable"):
        Input(**bad_input)


# TESTS FOR REPORT_PATH

def test_report_path_does_not_exist(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["report_path"] = "/no/such/report_dir"
    with pytest.raises(ValidationError, match="does not exist"):
        Input(**bad_input)


def test_report_path_is_file(minimal_valid_input, tmp_csv_file):
    bad_input = minimal_valid_input.copy()
    bad_input["report_path"] = tmp_csv_file
    with pytest.raises(ValidationError, match="is not a directory"):
        Input(**bad_input)


def test_report_path_not_writable(minimal_valid_input, tmp_path):
    ro_dir = tmp_path / "ro_reports"
    ro_dir.mkdir()
    os.chmod(ro_dir, 0o500)
    bad_input = minimal_valid_input.copy()
    bad_input["report_path"] = str(ro_dir)
    with pytest.raises(ValidationError, match="is not writable"):
        Input(**bad_input)


# TESTS FOR SHAPE MISMATCH (features_cols)

def test_features_cols_shape_warning(minimal_valid_input, tmp_path):
    file_path = tmp_path / "square_dataset.csv"
    file_path.write_text("id,col1,col2,col3\ns1,A,B,C\ns2,D,E,F\n", encoding="utf-8")
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(file_path)
    bad_input["dtypes"] = {"col1":"str","col2":"str","col3":"str"}
    with pytest.raises(DatasetShapeWarning, match="features might be in rows"):
        Input(**bad_input)


def test_shape_override_avoids_warning(minimal_valid_input, tmp_path):
    file_path = tmp_path / "square_dataset.csv"
    file_path.write_text("id,col1,col2,col3\ns1,A,B,C\ns2,D,E,F\n", encoding="utf-8")
    good_input = minimal_valid_input.copy()
    good_input["dataset_path"] = str(file_path)
    good_input["dtypes"] = {"col1":"str","col2":"str","col3":"str"}
    good_input["shape_override"] = True
    model = Input(**good_input)
    assert model.shape_override is True


# TESTS FOR en_header

def test_en_header_invalid_columns(minimal_valid_input, tmp_path):
    file_path = tmp_path / "weird_cols.csv"
    file_path.write_text("id,FakéCol\ns1,val1\ns2,val2\n", encoding="utf-8")
    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(file_path)
    with pytest.raises(ValidationError, match="Invalid column names detected"):
        Input(**bad_input)


def test_en_header_invalid_rows(minimal_valid_input, tmp_path):
    file_path = tmp_path / "weird_rows.csv"
    file_content = "FakeCol\n" "val1\n" "val2á\n"
    file_path.write_text(file_content, encoding="utf-8")

    bad_input = minimal_valid_input.copy()
    bad_input["dataset_path"] = str(file_path)
    with pytest.raises(ValidationError, match="Invalid row index values detected"):
        Input(**bad_input)


# TESTS FOR DTYPES

def test_dtypes_column_not_in_dataset(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["dtypes"] = {"NotARealColumn": "str"}
    with pytest.raises(ValidationError, match="column 'NotARealColumn' not found"):
        Input(**bad_input)


def test_dtypes_invalid_dtype(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["dtypes"] = {"col1": "invalid_dtype"}
    with pytest.raises(ValidationError, match="invalid dtype 'invalid_dtype'"):
        Input(**bad_input)


# TESTS FOR steps_to_run

def test_steps_to_run_unknown_step(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["steps_to_run"] = [{"step": "invalid_step"}]
    with pytest.raises(ValidationError, match="unknown step 'invalid_step'"):
        Input(**bad_input)


def test_steps_to_run_out_of_order(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    steps = [
        {"step": "handle_missing_values"},
        {"step": "identify_missing_values"}
    ]
    bad_input["steps_to_run"] = steps
    with pytest.raises(ValidationError, match="is out of order"):
        Input(**bad_input)


def test_steps_to_run_method_required_not_provided(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["steps_to_run"] = [{"step": "handle_outliers"}]
    with pytest.raises(ValidationError, match="invalid method 'None'"):
        Input(**bad_input)


def test_steps_to_run_invalid_method(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["steps_to_run"] = [{"step": "handle_outliers", "method": "INVALID"}]
    with pytest.raises(ValidationError, match="invalid method 'INVALID'"):
        Input(**bad_input)


def test_steps_to_run_extra_method_where_not_supported(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["steps_to_run"] = [
        {"step": "identify_missing_values", "method": "zscore"}
    ]
    with pytest.raises(ValidationError, match="does not support methods"):
        Input(**bad_input)


# TESTS FOR is_raw = True (REQUIRES FULL STEPS)

def test_is_raw_true_incomplete_steps(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    bad_input["steps_to_run"] = [
        {"step": "identify_missing_values"}
    ]
    with pytest.raises(ValidationError, match="steps_to_run error"):
        Input(**bad_input)


def test_is_raw_true_wrong_order(minimal_valid_input):
    bad_input = minimal_valid_input.copy()
    steps = bad_input["steps_to_run"][:]
    steps[0], steps[1] = steps[1], steps[0]
    bad_input["steps_to_run"] = steps
    with pytest.raises(ValidationError, match="steps_to_run error"):
        Input(**bad_input)

