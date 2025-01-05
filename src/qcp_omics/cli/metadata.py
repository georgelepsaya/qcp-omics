import click
from .handle_execution import handle_execution
from ..utils.utils import handle_json_input

@click.command()
@click.argument(
    "input_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    )
)
def metadata(input_path: str) -> None:
    """
    CLI command to process metadata from a specified JSON file.

    This command reads a metadata file from the given path, parses its
    JSON content, and processes the data using the `handle_execution` function.

    Args:
        input_path (str): Path to the input JSON metadata file.

    Raises:
        ClickException: If there are issues reading the file or processing its content.
    """
    try:
        click.echo(f"Reading input from a metadata file: {input_path}")

        # Parse the input JSON file
        input_json = handle_json_input(input_path)

        # Handle execution with the parsed JSON
        handle_execution(input_json)

    except Exception as e:
        raise click.ClickException(f"An error occurred: {e}")
