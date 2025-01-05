import typing as t
import click
from .input_validation import DatasetShapeWarning, Input
from pydantic import ValidationError
from qcp_omics.models.clinical_data import ClinicalData
from qcp_omics.models.genomics_data import GenomicsData
from qcp_omics.models.proteomics_data import ProteomicsData
from qcp_omics.utils.utils import load_dataset
from qcp_omics.report_generation.generate_report import generate_html_report

def instantiate_input(metadata: dict[str, t.Any]) -> Input:
    """
    Attempt to create the Input model, handling validation errors and dataset shape warnings.

    Args:
        metadata (dict[str, t.Any]): Metadata dictionary containing dataset configuration.

    Returns:
        Input: A validated Input model instance.

    Raises:
        SystemExit: If validation fails or user declines to override shape mismatch warning.
    """
    try:
        model = Input(**metadata)
    except ValidationError as ve:
        errors = ve.errors()
        click.echo(f"\nFound {len(errors)} validation error(s):")
        for error in errors:
            click.echo(f"  - {error['msg']}")
        raise SystemExit("Input validation failed. Exiting...")
    except DatasetShapeWarning as shape_warning:
        click.echo(f"\nWarning: {shape_warning}")
        if not click.confirm(
            "Dataset shape may be inconsistent with 'features_cols'. Continue anyway?",
            default=True
        ):
            raise SystemExit("Dataset shape validation failed. Exiting...")

        # If user confirmed, set shape_override = True, then retry.
        metadata["shape_override"] = True
        try:
            model = Input(**metadata)
        except ValidationError as ve2:
            errors = ve2.errors()
            click.echo(f"\nFound {len(errors)} validation error(s) on second attempt:")
            for error in errors:
                click.echo(f"  - {error['msg']}")
            raise SystemExit("Input validation failed. Exiting...")
        except DatasetShapeWarning as shape_warning2:
            click.echo(f"\nWarning: {shape_warning2}")
            raise SystemExit("Dataset shape validation still failed. Exiting...")

        click.echo("Shape mismatch warning overridden. Input validation successful.")
        return model
    else:
        # No exceptions raised
        click.echo("Input validation successful.")
        return model

def handle_execution(metadata: dict[str, t.Any]) -> None:
    """
    Execute the data processing pipeline based on provided metadata.

    Args:
        metadata (dict[str, t.Any]): Metadata dictionary containing dataset configuration.

    Raises:
        ValueError: If the dataset type in the metadata is unsupported.
    """
    metadata_model = instantiate_input(metadata)
    data = load_dataset(metadata_model.dataset_path)
    valid_metadata = metadata_model.model_dump()

    dataset_type_to_class = {
        "clinical": ClinicalData,
        "genomics": GenomicsData,
        "proteomics": ProteomicsData
    }

    dataset_model_class = dataset_type_to_class.get(valid_metadata['dataset_type'])
    if not dataset_model_class:
        raise ValueError(f"Unsupported dataset type: {valid_metadata['dataset_type']}")

    data_model = dataset_model_class(data, valid_metadata)
    data_model.transpose()
    data_model.map_dtypes()
    data_model.execute_steps()

    generate_html_report(
        data_model.report_data,
        valid_metadata,
        valid_metadata["report_path"]
    )

    data_model.save_data_files()
