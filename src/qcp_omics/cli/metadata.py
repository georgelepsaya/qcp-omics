import click
from .handle_execution import handle_execution
from ..utils.utils import handle_json_input


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
