from click.testing import CliRunner
from qcp_omics.cli.cli import qcp


def test_interactive_basic_flow(monkeypatch, tmp_path):
    runner = CliRunner()
    metadata_file = tmp_path / "test_metadata.json"
    metadata_file.write_text('{"dtypes":{"col1":"str","col2":"str"}}', encoding="utf-8")

    dataset_path = tmp_path / "test_dataset.csv"
    dataset_path.write_text("id,col1,col2\nsmpl1,v1,v2\nsmpl2,v3,v4\nsmpl3,v5,v6\n",
                            encoding="utf-8")

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

    assert "Welcome to QCP-Omics" in result.output
    assert "Steps to be run (in this order):" in result.output
    assert "Input validation successful." in result.output or "Shape mismatch warning overridden." in result.output


# def test_interactive_full_flow(monkeypatch, tmp_path):
#     runner = CliRunner()
#     metadata_file = tmp_path / "test_metadata.json"
#
