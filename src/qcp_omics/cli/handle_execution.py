import typing as t
import click
from .input_validation import DatasetShapeWarning, Input
from pydantic import ValidationError
from qcp_omics.models.clinical_data import ClinicalData
from qcp_omics.models.genomics_data import GenomicsData
from qcp_omics.utils.utils import load_dataset
from qcp_omics.models.proteomics_data import ProteomicsData
from qcp_omics.report_generation.generate_report import generate_html_report


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
    valid_metadata = metadata_model.model_dump()
    dataset_type_to_class = {
        "clinical": ClinicalData,
        "genomics": GenomicsData,
        "proteomics": ProteomicsData
    }
    dataset_model_class = dataset_type_to_class.get(valid_metadata['dataset_type'], {})
    if not dataset_model_class:
        raise ValueError(f"Unsupported dataset type: {valid_metadata['dataset_type']}")

    data_model = dataset_model_class(data, valid_metadata)
    data_model.transpose()
    data_model.map_dtypes()
    data_model.execute_steps()
    generate_html_report(data_model.report_data, valid_metadata, valid_metadata["report_path"])
