import click

@click.command()
def qcp() -> None:
    click.echo("Welcome to QCP-Omics\n")

    dataset: str = click.prompt("Path to the source dataset", type=str)
    output_dir: str = click.prompt("Path to the directory where output should be saved", type=str)
    features_cols: bool = click.confirm("Are features in columns and samples in rows in the input dataset?",
                                  default=None)

    en_headers: bool = click.confirm("Are all headers in English?", default=None)
    all_numeric: bool = click.confirm("Is all data numeric?", default=None)

    # if not all_numeric:


