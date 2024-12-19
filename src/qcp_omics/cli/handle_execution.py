import typing as t
import click
from .input_validation import DatasetShapeWarning, Input
from pydantic import ValidationError


def handle_execution(metadata: dict[str, t.Any]):
    try:
        metadata_model = Input(**metadata)
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
