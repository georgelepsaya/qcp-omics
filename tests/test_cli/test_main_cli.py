from click.testing import CliRunner
from qcp_omics.cli.cli import qcp


def test_qcp_no_args_shows_help():
    runner = CliRunner()
    result = runner.invoke(qcp, [])
    assert "Usage: qcp [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Welcome to QCP-Omics." in result.output


def test_qcp_help_option():
    runner = CliRunner()
    result = runner.invoke(qcp, ["--help"])
    assert result.exit_code == 0
    assert "Usage: qcp [OPTIONS] COMMAND [ARGS]..." in result.output


def test_qcp_interactive_help():
    runner = CliRunner()
    result = runner.invoke(qcp, ["interactive", "--help"])
    assert result.exit_code == 0
    assert "Usage: qcp interactive" in result.output


def test_qcp_metadata_help():
    runner = CliRunner()
    result = runner.invoke(qcp, ["metadata", "--help"])
    assert result.exit_code == 0
    assert "Usage: qcp metadata [OPTIONS] INPUT_PATH" in result.output
