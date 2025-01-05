import click
import pandas as pd
import os
import json
from typing import Any, List, Dict


def load_dataset(dataset_path: str) -> pd.DataFrame:
    """
    Load a dataset from a file path, supporting CSV and TSV formats.

    Args:
        dataset_path (str): Path to the dataset file.

    Returns:
        pd.DataFrame: Loaded dataset as a pandas DataFrame.

    Raises:
        ValueError: If the file extension is not supported.
    """
    _, ext = os.path.splitext(dataset_path)
    sep = "," if ext == ".csv" else "\t"
    if ext not in [".csv", ".tsv"]:
        raise ValueError(f"Unsupported file extension: {ext}")

    return pd.read_table(dataset_path, sep=sep, index_col=0)


def handle_json_input(input_path: str) -> Dict[str, Any]:
    """
    Load and validate a JSON metadata file.

    Args:
        input_path (str): Path to the JSON file.

    Returns:
        Dict[str, Any]: Parsed JSON data.

    Raises:
        click.UsageError: If the file is not a valid JSON file or cannot be read.
    """
    _, ext = os.path.splitext(input_path)
    if ext != ".json":
        raise click.UsageError("Metadata file must be a JSON file.")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise click.UsageError(f"Could not open file: {e}")


def prompt_already_run_steps(active_steps: List[Dict[str, Any]]) -> List[str]:
    """
    Prompt the user to select steps that have already been run.

    Args:
        active_steps (List[Dict[str, Any]]): List of active steps.

    Returns:
        List[str]: Names of steps already run, as chosen by the user.
    """
    if not active_steps:
        return []

    click.echo("\nSelect steps already run (comma-separated names).")
    click.echo("Available steps:")
    for step_dict in active_steps:
        click.echo(f"  - {step_dict['step']}")

    user_input = click.prompt(
        "\nEnter step names (comma separated). Press Enter to skip if none.",
        default="", show_default=False
    ).strip()

    if not user_input:
        return []

    chosen_step_names = [s.strip() for s in user_input.split(",") if s.strip()]
    valid_step_names = [step["step"] for step in active_steps]

    for name in chosen_step_names:
        if name not in valid_step_names:
            raise click.BadParameter(f"'{name}' is not a valid step in the pipeline.")

    return chosen_step_names


def remove_previous_steps(
        active_steps: List[Dict[str, Any]],
        previous_steps: List[str]
) -> None:
    """
    Remove previously run steps from the active steps list.

    Args:
        active_steps (List[Dict[str, Any]]): List of active steps.
        previous_steps (List[str]): Steps to remove.
    """
    active_steps[:] = [
        step_dict for step_dict in active_steps
        if step_dict["step"] not in previous_steps
    ]


def prompt_steps_to_run(active_steps: List[Dict[str, Any]]) -> List[int]:
    """
    Prompt the user to select steps to run from a list of active steps.

    Args:
        active_steps (List[Dict[str, Any]]): List of active steps.

    Returns:
        List[int]: Indices of steps to run.

    Raises:
        click.BadParameter: If the user input is invalid.
    """
    if not active_steps:
        click.echo("No active steps to run.")
        return []

    click.echo("\nSelect steps to run (in order):")
    for i, step_dict in enumerate(active_steps, start=1):
        click.echo(f"{i}. {step_dict['step']}")

    prompt_text = (
        "\nEnter 'all' to run all steps, or 'N' for a single step, or 'start-end' for a range (e.g., 1-3)."
    )
    user_input = click.prompt(prompt_text, type=str).strip().lower()

    max_index = len(active_steps)

    if user_input == "all":
        return list(range(max_index))

    if user_input.isdigit():
        num = int(user_input)
        if not 1 <= num <= max_index:
            raise click.BadParameter(f"Step number must be between 1 and {max_index}")
        return [num - 1]

    if "-" in user_input:
        parts = user_input.split("-")
        if len(parts) != 2:
            raise click.BadParameter("Invalid range format. Use 'start-end' (e.g., '1-3').")
        start_str, end_str = parts
        if not (start_str.isdigit() and end_str.isdigit()):
            raise click.BadParameter("Range must be numeric (e.g., '1-3').")

        start_idx = int(start_str)
        end_idx = int(end_str)
        if not 1 <= start_idx <= max_index or not 1 <= end_idx <= max_index:
            raise click.BadParameter(f"Range must be within 1 and {max_index}.")
        if start_idx > end_idx:
            raise click.BadParameter("Start of range cannot be larger than end of range.")

        return list(range(start_idx - 1, end_idx))

    raise click.BadParameter("Invalid input. Please enter 'all', or a single number, or 'start-end'.")


def prompt_methods_if_needed(step_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prompt the user to select a method for a given step, if applicable.

    Args:
        step_dict (Dict[str, Any]): A dictionary containing step information.

    Returns:
        Dict[str, Any]: The step information, potentially including the chosen method.
    """
    step_name = step_dict["step"]
    step_methods = step_dict.get("methods")

    if not step_methods or not isinstance(step_methods, list):
        return {"step": step_name}

    click.echo(f"\n'{step_name}' has multiple methods available:")
    for i, method_name in enumerate(step_methods, start=1):
        click.echo(f"{i}. {method_name}")

    choice = click.prompt(
        f"Choose a method for step '{step_name}'",
        type=click.Choice([str(i) for i in range(1, len(step_methods) + 1)]),
        show_choices=False
    )
    chosen_method = step_methods[int(choice) - 1]

    return {"step": step_name, "method": chosen_method}
