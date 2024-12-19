import click
from .interactive import interactive
from .metadata import metadata


@click.group()
def qcp():
    """Welcome to QCP-Omics."""
    pass


qcp.add_command(interactive, name="interactive")
qcp.add_command(metadata, name="metadata")
