import typing as t
import click
from .input_validation import DatasetShapeWarning, Input
from pydantic import ValidationError
from qcp_omics.omics_data import OmicsData
from .utils import load_dataset


def instantiate_input(metadata: dict[str, t.Any]) -> Input:
    try:
        metadata_model = Input(**metadata)
    except ValidationError as validation_error:
        errors = validation_error.errors()
        click.echo(f"\nFound {len(errors)} validation error(s):")
        for error in errors:
            click.echo(error["msg"])
        raise SystemExit("Input validation failed. Exiting...")
    except DatasetShapeWarning as shape_warning:
        click.echo(f"Warning: {shape_warning}")
        if not click.confirm(
                "Confirm that features are in columns and samples are in rows",
                default=True
        ):
            raise SystemExit("Dataset shape validation failed. Exiting...")
    else:
        click.echo("Input validation successful.")
        return metadata_model


def handle_execution(metadata: dict[str, t.Any]) -> None:
    metadata_model = instantiate_input(metadata)
    data = load_dataset(metadata_model.dataset_path)
    metadata = metadata_model.model_dump()
    data_model = OmicsData(data, metadata)
    print(data_model)
