import click
import typing as t
import copy
from .input_validation import DatasetShapeWarning, Input
from pydantic import ValidationError
from .interactive_utils import echo_steps, validate_steps, update_previous_steps, get_steps_to_run


cli_input: dict[str, t.Any] = dict()

all_steps: dict[str, list[str]] = {
    "qc_steps": [
        "identify_missing_values",
        "detect_outliers",
    ],
    "preprocessing_steps": [
        "handle_missing_values",
        "handle_outliers",
        "normalize_numerical_features",
        "transform",
        "encode_categorical_variables",
        "scale_features",
        "dimensionality_reduction"
    ],
    "visualization_steps": [
        "distribution_numerical",
        "distribution_categorical",
        "visualize_outliers",
        "correlation_heatmaps",
        "correlation_heatmaps",
        "feature_interdependencies",
        "categorical_feature_relationships",
        "visualize_dimensionality_reduction"
    ],
    "analysis_steps": [
        "descriptive_statistics",
        "group_comparisons",
        "correlation_coefficients",
        "multicollinearity",
        "build_models",
        "evaluate_model_performance",
        "feature_importance_analysis",
        "hypothesis_testing"
    ],
}

previous_steps: dict[str, list[str]] = {
    "qc_steps": [],
    "preprocessing_steps": [],
    "visualization_steps": [],
    "analysis_steps": []
}


@click.command()
def interactive() -> None:
    click.echo("Welcome to QCP-Omics")

    dataset_type_options: list[str] = ["genomics", "proteomics", "clinical"]
    click.echo("\nWhat is the input dataset type:")
    for i, option in enumerate(dataset_type_options, 1):
        click.echo(f"{i}. {option}")
    choice = click.prompt("Choose one (1-3)", type=click.Choice(["1", "2", "3"]), show_choices=False)
    cli_input["dataset_type"] = dataset_type_options[int(choice) - 1]
    cli_input["dataset_path"] = click.prompt("\nPath to the source dataset", type=str)
    cli_input["metadata_path"] = click.prompt("\nPath to the metadata file", type=str)
    cli_input["output_path"] = click.prompt("\nPath to the directory where output should be saved", type=str)
    cli_input["features_cols"] = click.confirm("\nAre features in columns and samples in rows in the input dataset?",
                                               default=True)
    cli_input["en_header"] = click.confirm("\nAre all values in header and index in English?", default=True)
    cli_input["all_numeric"] = click.confirm("\nIs all data numeric?")

    is_raw: bool = click.confirm("\nIs data raw (no processing applied yet)?", default=True)
    cli_input["is_raw"] = is_raw

    active_steps = copy.deepcopy(all_steps)
    total_steps: int

    if not is_raw:
        click.echo("\nSelect steps already run:")
        total_steps = echo_steps(active_steps, previous_steps)
        steps = click.prompt(
            "\nChoose run steps (comma-separated, e.g., 1,2,3)",
            type=str
        )
        update_previous_steps(validate_steps(steps, total_steps, "previous"), active_steps, previous_steps)
        click.echo("Previous steps you chose:")
        for s in previous_steps:
            click.echo(f"\t- {s}")

    click.echo("\nSelect steps you want to run:")
    click.echo("0. run all steps in the given order")
    total_steps = echo_steps(active_steps, previous_steps)
    steps = click.prompt(
        "\nChoose steps in desired order (comma-separated, e.g. 1,2,3) or 0 to select all in given order",
        type=str
    )

    validated_steps = validate_steps(steps, total_steps, "to_run")
    steps_to_run: list[str]

    if len(validated_steps) == 1 and 0 in validated_steps:
        steps_to_run = get_steps_to_run([i + 1 for i in range(total_steps)], active_steps)
    else:
        steps_to_run = get_steps_to_run(validated_steps, active_steps)
    click.echo("Steps to be run:")
    for s in steps_to_run:
        click.echo(f"\t- {s}")

    cli_input["steps_to_run"] = steps_to_run

    try:
        input_model = Input(**cli_input)
    except ValidationError as validation_error:
        errors = validation_error.errors()
        click.echo(f"\nFound {len(errors)} error(s):")
        for error in errors:
            message = error["msg"]
            click.echo(message)
        raise SystemExit("Input validation failed due to errors above. Exiting...")
    except DatasetShapeWarning as e:
        click.echo(f"Found a warning: {e}")
        confirm_shape: bool = click.confirm("Confirm that that features are indeed in columns and samples in rows",
                      default=True)
        if not confirm_shape:
            raise SystemExit("Validation failed due to incorrect shape of the provided dataset. Exiting...")

    click.echo("Input validation successful. Proceeding with selected steps...")
