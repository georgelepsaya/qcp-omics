import pytest
from click.testing import CliRunner
from qcp_omics.cli.cli import qcp


metadata_base = """{
    "dataset_type": "proteomics",
    "dataset_path": "%(ds_path)s",
    "metadata_path": "%(md_path)s",
    "output_path": "%(out_path)s",
    "report_path": "%(out_path)s",
    "features_cols": true,
    "en_header": true,
    "is_raw": true,
    "dtypes": %(dtypes)s,
    "steps_to_run": [
        {"step": "identify_missing_values"},
        {"step": "handle_missing_values"},
        {"step": "handle_outliers", "method": "IQR"},
        {"step": "split_train_test"},
        {"step": "split_numerical_categorical"},
        {"step": "scale_numerical_features", "method": "standard_scaler"},
        {"step": "transform_numerical_features", "method": "box-cox"},
        {"step": "descriptive_statistics"},
        {"step": "pairwise_correlations_numerical", "method": "pearson"},
        {"step": "evaluate_distribution_features"},
        {"step": "dimensionality_reduction"}
    ]
}
"""


def write_test_files(tmp_path, dataset_content):
    dataset_path = tmp_path / "test_dataset.csv"
    dataset_path.write_text(dataset_content, encoding="utf-8")

    return dataset_path


@pytest.mark.parametrize("dataset_content,dtypes", [
    ("id,col1,col2\nsmpl1,v1,v2\nsmpl2,v3,v4\nsmpl3,v5,v6\n", '{"col1":"str","col2":"str"}'),
    ("id,col1,col2,col3,col4\ns1,c1,4.5,c2,1.2\ns2,c3,1.3,c4,6.5\ns3,c5,1.8,c6,8.6\ns4,c7,3.3,c8,4.3\ns5,c9,5.5,c10,3.4\n",
     '{"col1":"category","col2":"float","col3":"category","col4":"float"}')
])
def test_metadata_command_valid_json(tmp_path, dataset_content, dtypes):
    runner = CliRunner()
    dataset_path = write_test_files(tmp_path, dataset_content)
    output_path = tmp_path / "out"
    output_path.mkdir(exist_ok=True)
    metadata_file = tmp_path / "input.json"
    metadata_file.write_text(metadata_base % {
        "ds_path": dataset_path,
        "md_path": metadata_file,
        "out_path": output_path,
        "dtypes": dtypes
    }, encoding="utf-8")

    result = runner.invoke(qcp, ["metadata", str(metadata_file)])
    assert result.exit_code == 0, f"Command failed unexpectedly: {result.output}"
    assert "Input validation successful." in result.output or "Shape mismatch warning overridden." in result.output
