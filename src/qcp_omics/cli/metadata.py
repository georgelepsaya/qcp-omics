import click
import typing as t
import os
import json
from .handle_execution import handle_execution


def handle_json_input(input_path: str) -> dict[str, t.Any]:
    _, ext = os.path.splitext(input_path)
    if ext != ".json":
        raise click.UsageError("Metadata file must be a JSON file.")
    try:
        with open(input_path, "r") as f:
            input_metadata = json.load(f)
    except json.JSONDecodeError as e:
        raise click.UsageError(f"Invalid JSON file: {e}")
    return input_metadata


@click.command()
@click.argument("input_path",
                type=click.Path(exists=True,
                                file_okay=True,
                                dir_okay=False,
                                readable=True))
def metadata(input_path) -> None:
    click.echo(f"Reading input from a metadata file: {input_path}")
    input_json = handle_json_input(input_path)
    handle_execution(input_json)
