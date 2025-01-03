from click.testing import CliRunner
from qcp_omics.cli.cli import qcp
import pytest


def write_test_files(tmp_path, metadata_content, dataset_content):
    metadata_file = tmp_path / "test_metadata.json"
    metadata_file.write_text(metadata_content, encoding="utf-8")

    dataset_path = tmp_path / "test_dataset.csv"
    dataset_path.write_text(dataset_content, encoding="utf-8")

    return metadata_file, dataset_path

@pytest.mark.parametrize("metadata_content, dataset_content", [
    (
        '{"dtypes":{"col1":"str","col2":"str"}}',
        "id,col1,col2\nsmpl1,v1,v2\nsmpl2,v3,v4\nsmpl3,v5,v6\n",
    ),
    (
        '{"dtypes":{"col1":"category","col2":"float","col3":"category","col4":"float"}}',
        "id,col1,col2,col3,col4\ns1,c1,4.5,c2,1.2\ns2,c3,1.3,c4,6.5\ns3,c5,1.8,c6,8.6\ns4,c7,3.3,c8,4.3\ns5,c9,5.5,c10,3.4\n",
    ),
])
def test_interactive_flow(tmp_path, metadata_content, dataset_content):
    runner = CliRunner()
    metadata_file, dataset_path = write_test_files(tmp_path, metadata_content, dataset_content)

    user_input = "\n".join([
        "1",
        str(dataset_path),
        str(metadata_file),
        str(tmp_path),
        "y",
        "y",
        "y",
        "all",
        "1",
        "1",
        "1",
        "1"
    ]) + "\n"

    result = runner.invoke(qcp, ["interactive"], input=user_input)
    assert result.exit_code == 0, f"Command failed: {result.output}"
    assert "Welcome to QCP-Omics" in result.output
    assert "Steps to be run (in this order):" in result.output
    assert "Input validation successful." in result.output or "Shape mismatch warning overridden." in result.output
