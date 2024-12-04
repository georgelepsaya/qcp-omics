import click
from pydantic import BaseModel
from typing import List


class Input(BaseModel):
    dataset_type: str
    dataset_path: str
    output_path: str
    features_cols: bool
    en_headers: bool
    all_numeric: bool


qc_steps: List[str] = ["identify_missing_values", "impute_continuous"]
preprocessing_steps: List[str] = ["transform", "normalize", "scale"]
visualization_steps: List[str] = ["visualization"]
analysis_steps: List[str] = ["correlation", "regression", "pca"]
all_steps: List[str] = qc_steps + preprocessing_steps + visualization_steps + analysis_steps
previous_steps: List[str] = []


def echo_steps() -> int:
    steps = [s for s in all_steps if s not in previous_steps]
    for i, step in enumerate(steps):
        if i == 0:
            click.echo("QC steps:")
        elif i == len(qc_steps):
            click.echo("Preprocessing steps:")
        elif i == len(qc_steps + preprocessing_steps):
            click.echo("Visualization steps:")
        elif i == len(qc_steps + preprocessing_steps + visualization_steps):
            click.echo("Analysis steps:")
        click.echo(f"{i + 1}. {step}")
    return len(steps)


def validate_steps(steps: str, num_steps: int) -> List[int]:
    try:
        selected = [int(s.strip()) for s in steps.split(',')]
        if not all(0 <= s <= num_steps for s in selected):
            raise ValueError("All steps must be within given range")
        return selected
    except ValueError as e:
        raise click.BadParameter(f"Invalid input: {e}")



@click.command()
def qcp() -> None:
    click.echo("Welcome to QCP-Omics")

    cli_input: dict = dict()

    dataset_type_options = ["genomics", "proteomics", "clinical"]
    click.echo("\nWhat is the input dataset type:")
    for i, option in enumerate(dataset_type_options, 1):
        click.echo(f"{i}. {option}")
    choice = click.prompt("Choose one (1-3)", type=click.Choice(["1", "2", "3"]), show_choices=False)
    cli_input["dataset_type"] = dataset_type_options[int(choice) - 1]
    cli_input["dataset_path"] = click.prompt("\nPath to the source dataset", type=str),
    cli_input["output_path"] = click.prompt("\nPath to the directory where output should be saved", type=str),
    cli_input["features_cols"] = click.confirm("\nAre features in columns and samples in rows in the input dataset?",
                                               default=True)
    cli_input["en_headers"] = click.confirm("\nAre all headers in English?", default=True)
    cli_input["all_numeric"] = click.confirm("\nIs all data numeric?")

    is_raw = click.confirm("\nIs data raw (no processing applied yet)?", default=True)

    if not is_raw:
        click.echo("\nSelect steps already run:")
        num_steps = echo_steps()
        steps = click.prompt(
            "\nChoose run steps (comma-separated, e.g., 1,2,3)",
            type=str
        )

        global previous_steps
        previous_steps = [all_steps[i-1] for i in validate_steps(steps, num_steps)]
        click.echo("Previous steps you chose:")
        for s in previous_steps:
            click.echo(f"\t- {s}")

    click.echo("\nSelect steps you want to run:")
    num_steps = echo_steps()
    steps = click.prompt(
        "\nChoose steps in desired order (comma-separated, e.g. 1,4,3) or 0 to select all in given order",
        type=str
    )
    steps_to_run = [all_steps[i-1] for i in validate_steps(steps, num_steps)]
    click.echo("Steps to be run:")
    for s in steps_to_run:
        click.echo(f"\t- {s}")



# - input:
#     data_matrix: "your/data/matrix/path"
#     dataset_type: "clinical/genomics/proteomics/metabolomics"
#     current_preprocessing_level: "raw/filtered/normalised/transformed/scaled"
#     steps:
#         - identify_missing_values
#         - impute_continuous
#         - ... or simply
#         - qc_all
#         - etc.
#     output_matrix: "output/matrix/path"
#     output_report: "output/report/path"
#     output_log: "output/log/path"
