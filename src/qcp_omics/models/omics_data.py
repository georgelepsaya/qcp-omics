from abc import ABC
from typing import Optional, List, Dict, Any
import pandas as pd
import click
from pathlib import Path

class OmicsData(ABC):
    """
    A class for managing and processing omics datasets with associated metadata.

    Attributes:
        data (pd.DataFrame): The primary dataset.
        data_numerical (Optional[pd.DataFrame]): Subset of the dataset containing numerical data.
        data_categorical (Optional[pd.DataFrame]): Subset of the dataset containing categorical data.
        test_set (Optional[pd.DataFrame]): A test split of the dataset for testing models.
        metadata (dict): Metadata associated with the dataset, including dtypes and processing steps.
        report_data (List[Dict]): A collection of report data for further analysis.
    """

    def __init__(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> None:
        """
        Initialize the OmicsData instance.

        Args:
            data (pd.DataFrame): The primary dataset.
            metadata (Dict[str, Any]): Metadata containing additional information about the dataset.
        """
        self.data: pd.DataFrame = data
        self.data_numerical: Optional[pd.DataFrame] = None
        self.data_categorical: Optional[pd.DataFrame] = None
        self.test_set: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = metadata
        self.report_data: List[Dict] = []

    def __repr__(self) -> str:
        """
        String representation of the OmicsData instance.

        Returns:
            str: A string summarizing the dataset type from the metadata.
        """
        return f"<OmicsData(dataset_type: {self.metadata.get('dataset_type', 'Unknown')})>"

    def transpose(self) -> None:
        """
        Transpose the dataset if the metadata indicates features are not in columns.
        """
        if not self.metadata.get("features_cols", True):
            click.echo("Transposing the dataset")
            self.data = self.data.T

    def map_dtypes(self) -> None:
        """
        Map the data types of columns in the dataset based on the metadata.
        """
        click.echo("Mapping the dtypes from metadata with the dataset")
        dtype_mapping = self.metadata.get("dtypes", {})
        for col, dtype in dtype_mapping.items():
            if col in self.data.columns:
                try:
                    if dtype == "category":
                        self.data[col] = self.data[col].astype("category")
                    elif dtype == "int":
                        self.data[col] = self.data[col].astype("int")
                    elif dtype == "float":
                        self.data[col] = self.data[col].astype("float")
                except ValueError as e:
                    click.echo(f"Error casting column '{col}' to type '{dtype}': {e}")

    @staticmethod
    def _visualize_data_snapshot(df: pd.DataFrame) -> str:
        """
        Generate an HTML snapshot of the DataFrame for visualization purposes.

        Args:
            df (pd.DataFrame): The DataFrame to visualize.

        Returns:
            str: An HTML table representation of the DataFrame.
        """
        limited_df = df if len(df.index) <= 25 else df.head(25)

        return limited_df.to_html(classes="table table-striped table-bordered table-hover")

    def execute_steps(self) -> None:
        """
        Execute a series of processing steps as defined in the metadata.
        """
        steps = self.metadata.get("steps_to_run", [])
        for step in steps:
            step_name = step.get("step")
            method = step.get("method")
            if step_name:
                step_impl = getattr(self, step_name, None)
                if callable(step_impl):
                    if method:
                        click.echo(f"Executing step '{step_name}' with method '{method}'...")
                        step_impl(method=method)
                    else:
                        click.echo(f"Executing step '{step_name}'...")
                        step_impl()
                else:
                    click.echo(f"Step '{step_name}' is not recognized and will be skipped.")
            else:
                click.echo("Step definition is missing the 'step' key and will be skipped.")

    def save_data_files(self) -> None:
        """
        Save train and test data files in CSV format to the specified output path.
        - Combines `data_numerical` and `data_categorical` into a single train dataset if both are non-empty.
        - Saves `test_set` separately if it is not empty.

        Logs success or failure of each save operation.
        """

        out_path = Path(self.metadata["output_path"])
        out_path.mkdir(parents=True, exist_ok=True)

        train_path = out_path / "train_data.csv"
        test_path = out_path / "test_data.csv"

        try:
            if not self.data_numerical.empty or not self.data_categorical.empty:
                if not self.data_numerical.empty and not self.data_categorical.empty:
                    train_df = pd.concat([self.data_numerical, self.data_categorical], axis=1)
                else:
                    train_df = self.data_numerical if not self.data_numerical.empty else self.data_categorical

                train_df.to_csv(train_path, index=False)
                click.echo(f"Train set successfully saved to {train_path}")
            else:
                click.echo(f"No train set created to be saved to {out_path}")

            if not self.test_set.empty:
                self.test_set.to_csv(test_path, index=False)
                click.echo(f"Test set successfully saved to {test_path}")
            else:
                click.echo(f"No test set created to be saved to {out_path}")
        except Exception as e:
            click.echo(f"An error occurred while saving data files: {e}")
