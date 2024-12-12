import click
from pydantic import BaseModel, field_validator, model_validator, ValidationError
import copy
import os
import pandas as pd
import typing as t
from typing_extensions import Self
import re


class DatasetShapeWarning(Exception):
    def __init__(self, message: str, value: tuple[int, int]) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}: {self.value[0]} rows, {self.value[1]} columns."


class Input(BaseModel):
    dataset_type: str
    dataset_path: str
    output_path: str
    features_cols: bool
    en_header: bool
    all_numeric: bool
    is_raw: bool
    steps_to_run: list[str]

    def load_dataset(self) -> pd.DataFrame:
        dataset_path = self.dataset_path
        _, ext = os.path.splitext(dataset_path)
        sep = "," if ext == ".csv" else "\t"
        df = pd.read_table(dataset_path, sep=sep, index_col=0)
        return df

    @field_validator("dataset_type")
    @classmethod
    def check_dataset_type_value(cls, v: str) -> str:
        if v not in ["genomics", "proteomics", "clinical"]:
            raise ValueError("Incorrect dataset type value")
        return v

    @field_validator("dataset_path")
    @classmethod
    def check_dataset_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(f"Path '{v}' does not exist.")
        if not os.path.isfile(v):
            raise ValueError(f"Path '{v}' is not a file.")
        if not os.access(v, os.R_OK):
            raise ValueError(f"File '{v}' cannot be opened or read.")
        if os.path.getsize(v) == 0:
            raise ValueError(f"File '{v}' is empty.")
        _, ext = os.path.splitext(v)
        allowed_extensions = [".csv", ".tsv"]
        if ext.lower() not in allowed_extensions:
            raise ValueError(f"File '{v}' extension is not one of: {', '.join(allowed_extensions)}.")
        return v

    @field_validator("output_path")
    @classmethod
    def check_output_path(cls, v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(f"Output path '{v}' does not exist.")
        if not os.path.isdir(v):
            raise ValueError(f"Output path '{v}' is not a directory.")
        if not os.access(v, os.W_OK):
            raise ValueError(f"Directory '{v}' is not writable.")
        return v

    @model_validator(mode="after")
    def check_features_cols(self) -> Self:
        df = self.load_dataset()
        shape = df.shape
        # check for contradiction with specified shape
        if self.features_cols and shape[0] <= shape[1]:
            raise DatasetShapeWarning("Features may be in rows instead of columns due to detected shape", shape)
        elif not self.features_cols and shape[0] >= shape[1]:
            raise DatasetShapeWarning("Features may be in columns instead of rows due to detected shape", shape)
        return self

    @model_validator(mode="after")
    def check_en_headers(self) -> Self:
        df = self.load_dataset()
        columns = df.columns.to_list()
        rows = df.index.to_list()
        pattern = re.compile(r"^[a-zA-Z0-9 _\-]+$")
        if any(not pattern.match(item) for item in columns + rows):
            raise ValueError(f"Some values in header or index are not in English")
        return self


all_steps: dict[str, list[str]] = {
    "qc_steps": ["identify_missing_values", "impute_continuous"],
    "preprocessing_steps": ["transform", "normalize", "scale"],
    "visualization_steps": ["visualization"],
    "analysis_steps": ["correlation", "regression", "pca"],
}

previous_steps: dict[str, list[str]] = {
    "qc_steps": [],
    "preprocessing_steps": [],
    "visualization_steps": [],
    "analysis_steps": []
}


# update active steps, echo them and return amount of active steps
def echo_steps(active_steps: dict[str, list[str]]) -> int:
    for category, steps in previous_steps.items():
        if category in active_steps:
            active_steps[category] = [
                step for step in active_steps[category] if step not in steps
            ]
    step_number: int = 1
    for category, steps in active_steps.items():
        formatted_category = category.replace("_", " ").capitalize()
        click.echo(f"{formatted_category}:")
        for step in steps:
            click.echo(f"{step_number}. {step}")
            step_number += 1
    return step_number


# validate selected steps and return a list of numbers of steps
def validate_steps(steps: str, num_steps: int, stage: str) -> list[int]:
    try:
        selected: list[int] = [int(s.strip()) for s in steps.split(',')]
        if 0 in selected and stage == 'to_run':
            if len(selected) > 1:
                raise ValueError("Either select all steps with 0 or specify steps to run (e.g., 1,2,3)")
        if not all(1 <= s <= num_steps for s in selected if s != 0):
            raise ValueError(f"All steps must be within 1 and {num_steps}")
        return selected
    except ValueError as e:
        raise click.BadParameter(f"Invalid input: {e}")


def update_previous_steps(input_numbers: list[int], active: dict[str, list[str]], previous: dict[str, list[str]]) -> None:
    step_number: int = 1
    for category, steps in active.items():
        for step in steps:
            if step_number in input_numbers:
                previous[category].append(step)
            step_number += 1


def get_steps_to_run(validated_steps: list[int], active_steps: dict[str, list[str]]) -> list[str]:
    steps_to_run: list[str] = []
    step_number = 1
    for category, steps in active_steps.items():
        for step in steps:
            if step_number in validated_steps:
                steps_to_run.append(step)
            step_number += 1
    return steps_to_run


@click.command()
def qcp() -> None:
    click.echo("Welcome to QCP-Omics")

    cli_input: dict[str, t.Any] = dict()

    dataset_type_options: list[str] = ["genomics", "proteomics", "clinical"]
    click.echo("\nWhat is the input dataset type:")
    for i, option in enumerate(dataset_type_options, 1):
        click.echo(f"{i}. {option}")
    choice = click.prompt("Choose one (1-3)", type=click.Choice(["1", "2", "3"]), show_choices=False)
    cli_input["dataset_type"] = dataset_type_options[int(choice) - 1]
    cli_input["dataset_path"] = click.prompt("\nPath to the source dataset", type=str)
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
        total_steps = echo_steps(active_steps)
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
    total_steps = echo_steps(active_steps)
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
