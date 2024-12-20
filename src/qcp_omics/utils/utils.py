import click
import pandas as pd
import os


def load_dataset(dataset_path) -> pd.DataFrame:
    dataset_path = dataset_path
    _, ext = os.path.splitext(dataset_path)
    sep = "," if ext == ".csv" else "\t"
    df = pd.read_table(dataset_path, sep=sep, index_col=0)
    return df


# update active steps, echo them and return amount of active steps
def echo_steps(active_steps: dict[str, list[str]], previous_steps: dict[str, list[str]]) -> int:
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
