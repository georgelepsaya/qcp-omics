import copy
import click
import typing as t

from .handle_execution import handle_execution
from qcp_omics.utils.utils import (
    prompt_already_run_steps,
    remove_previous_steps,
    prompt_steps_to_run,
    prompt_methods_if_needed,
    handle_json_input
)

# Constants for pipeline steps
ALL_STEPS: list[dict] = [
    {"step": "identify_missing_values"},
    {"step": "handle_missing_values"},
    {"step": "handle_outliers", "methods": ["IQR", "zscore"]},
    {"step": "split_train_test"},
    {"step": "split_numerical_categorical"},
    {"step": "scale_numerical_features", "methods": ["standard_scaler", "robust_scaler"]},
    {"step": "transform_numerical_features", "methods": ["box-cox", "log2"]},
    {"step": "descriptive_statistics"},
    {"step": "pairwise_correlations_numerical", "methods": ["pearson", "spearman"]},
    {"step": "evaluate_distribution_features"},
    {"step": "dimensionality_reduction"}
]

PREVIOUS_STEPS: list[str] = []

@click.command()
def interactive() -> None:
    """
    Interactive command-line interface for configuring and running a QCP-Omics pipeline.

    Prompts the user to specify dataset details, choose steps to run, and configure options
    for each step. Then executes the pipeline with the selected configuration.
    """
    click.echo("Welcome to QCP-Omics")

    # Prompt user for dataset type
    dataset_type_options: list[str] = ["clinical", "genomics", "proteomics"]
    click.echo("\nWhat is the input dataset type:")
    for i, option in enumerate(dataset_type_options, 1):
        click.echo(f"{i}. {option}")
    choice = click.prompt("Choose one (1-3)", type=click.Choice(["1", "2", "3"]), show_choices=False)
    dataset_type = dataset_type_options[int(choice) - 1]

    # Gather dataset paths and options
    dataset_path: str = click.prompt("\nPath to the source dataset", type=str)
    metadata_path: str = click.prompt("\nPath to the metadata file", type=str)
    output_path: str = click.prompt("\nPath to the directory where output should be saved", type=str)
    features_cols: bool = click.confirm("\nAre features in columns and samples in rows in the input dataset?", default=True)
    en_header: bool = click.confirm("\nAre all values in header and index in English?", default=True)
    is_raw: bool = click.confirm("\nIs data raw (no processing applied yet)?", default=True)

    # Prepare the input dictionary for handle_execution
    cli_input: dict[str, t.Any] = {
        "dataset_type": dataset_type,
        "dataset_path": dataset_path,
        "metadata_path": metadata_path,
        "output_path": output_path,
        "report_path": output_path,
        "features_cols": features_cols,
        "en_header": en_header,
        "is_raw": is_raw
    }

    # Manage pipeline steps
    active_steps: list[dict] = copy.deepcopy(ALL_STEPS)

    if not is_raw:
        steps_already_run = prompt_already_run_steps(active_steps)
        PREVIOUS_STEPS.extend(steps_already_run)
        remove_previous_steps(active_steps, PREVIOUS_STEPS)

        click.echo("\nSteps already run (removed from the pipeline):")
        for step_name in steps_already_run:
            click.echo(f"  - {step_name}")

    # Prompt user for steps to run
    steps_indices_to_run = prompt_steps_to_run(active_steps)
    steps_to_run: list[dict[str, t.Any]] = []

    for idx in steps_indices_to_run:
        step_dict = active_steps[idx]
        step_to_run = prompt_methods_if_needed(step_dict)
        steps_to_run.append(step_to_run)

    click.echo("\nSteps to be run (in this order):")
    for step in steps_to_run:
        if "method" in step:
            click.echo(f"  - {step['step']}  (method: {step['method']})")
        else:
            click.echo(f"  - {step['step']}")

    # Load metadata and update input
    input_metadata: dict[str, t.Any] = handle_json_input(cli_input["metadata_path"])
    cli_input["dtypes"] = input_metadata["dtypes"]
    cli_input["steps_to_run"] = steps_to_run

    # Execute the pipeline
    handle_execution(cli_input)
