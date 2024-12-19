import click

@click.command()
def metadata() -> None:
    click.echo("Handle input from a metadata file")
