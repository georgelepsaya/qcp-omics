# QCP-Omics

![Tests](https://github.com/georgelepsaya/qcp-omics/actions/workflows/tests.yaml/badge.svg)


## Installation

### Singularity (on HPC) - _recommended_
1. Load singularity: `module load singularity`
2. Pull the image from docker: `singularity pull qcp-omics.sif docker://georgelepsaya/qcp-omics:latest`
3. Verify installation: `singularity run qcp-omics.sif`

### From PyPI

Requires Python version >= 3.11.

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install the tool: `pip install qcp-omics`
4. Verify installation: `qcp`

## Instructions

# QCP-Omics Usage

[TOC]

# Metadata File Guide for qcp-omics

## Overview

The `qcp-omics` tool (`qcp`) provides powerful capabilities for preprocessing and analyzing omics datasets. This guide explains how to create a metadata file required for running the tool in both interactive and metadata modes.

## Modes of Operation

### 1. Interactive Mode

**Command:**
```bash
qcp interactive
```

In this mode, users interactively input metadata through CLI prompts, except for data types (`dtypes`). The required JSON file must contain the `dtypes` field to specify the data types of dataset columns.

**Requirements:**
- Only the `dtypes` field is required; all other metadata will be collected during CLI interaction.
- Data types must be supported by pandas (e.g., `int`, `float`, `category`).

**Example `dtypes` JSON:**
```json
{
  "dtypes": {
    "age": "int",
    "gender": "category",
    "height": "float"
  }
}
```

### 2. Metadata Mode

**Command:**
```bash
qcp metadata path/to/metadata.json
```

In this mode, the entire preprocessing and analysis pipeline is executed automatically based on the provided metadata JSON file.

**Requirements:**
- All metadata fields must be fully specified.
- The order of preprocessing steps must follow a specific sequence.

## Metadata JSON Structure

### Metadata Fields

| Field               | Type                     | Description                                                                                  |
|--------------------|--------------------------|----------------------------------------------------------------------------------------------|
| `dataset_type`     | `string`                | Type of dataset: `clinical`, `genomics`, or `proteomics`.                                     |
| `dataset_path`     | `string`                | Path to the dataset file (`.csv` or `.tsv`).                                                 |
| `metadata_path`    | `string`                | Path to the metadata JSON file.                                                              |
| `output_path`      | `string`                | Path to store processed datasets.                                                            |
| `report_path`      | `string`                | Path to save the generated report.                                                           |
| `features_cols`    | `boolean`               | `true` if features are in columns and samples in rows; `false` to transpose the dataset.      |
| `en_header`        | `boolean`               | `true` if the header and index are alphanumeric.                                             |
| `is_raw`           | `boolean`               | `true` if the dataset is raw (unprocessed).                                                  |
| `steps_to_run`     | `list`                  | Ordered list of processing steps to execute (details below).                                 |
| `dtypes`           | `object`                | Mapping of dataset columns to their data types.                                              |

### Example Metadata JSON

```json
{
  "dataset_type": "genomics",
  "dataset_path": "data/genomics_data.csv",
  "metadata_path": "metadata/config.json",
  "output_path": "results/",
  "report_path": "results/",
  "features_cols": true,
  "en_header": true,
  "is_raw": true,
  "steps_to_run": [
    { "step": "identify_missing_values" },
    { "step": "handle_missing_values" },
    { "step": "handle_outliers", "method": "IQR" },
    { "step": "split_train_test" },
    { "step": "split_numerical_categorical" },
    { "step": "scale_numerical_features", "method": "standard_scaler" },
    { "step": "transform_numerical_features", "method": "box-cox" },
    { "step": "descriptive_statistics" },
    { "step": "pairwise_correlations_numerical", "method": "pearson" },
    { "step": "evaluate_distribution_features" },
    { "step": "dimensionality_reduction" }
  ],
  "dtypes": {
    "gene_expression": "float",
    "sample_id": "category"
  }
}
```

## Explanation of `steps_to_run`

### Full Pipeline (when `is_raw` is `true`)
All steps must be provided **in the exact order** listed below:

1. `identify_missing_values`
2. `handle_missing_values`
3. `handle_outliers` *(method required, e.g., `IQR`)*
4. `split_train_test`
5. `split_numerical_categorical`
6. `scale_numerical_features` *(method required, e.g., `standard_scaler`)*
7. `transform_numerical_features` *(method required, e.g., `box-cox`)*
8. `descriptive_statistics`
9. `pairwise_correlations_numerical` *(method required, e.g., `pearson`)*
10. `evaluate_distribution_features`
11. `dimensionality_reduction`

### Partial Pipeline (when `is_raw` is `false`)
Users can select any subset of steps but must maintain the **original order**. For example:

- Valid: `[3, 5, 6, 9]` → `handle_outliers`, `split_numerical_categorical`, `scale_numerical_features`, `pairwise_correlations_numerical`
- Invalid: `[3, 6, 5]` → `handle_outliers`, `scale_numerical_features`, `split_numerical_categorical` (Incorrect order)

## Output

- **Processed Data:**
  - `train_dataset.csv` and `test_dataset.csv` saved in `output_path`
- **Report:**
  - `report.html` saved in `report_path`

## Notes

- Ensure that all paths in the metadata JSON are correct and accessible.
- Data types in `dtypes` must align with pandas-supported types.
- Preprocessing steps must respect the defined sequence to maintain pipeline integrity.

---

For more information, visit the official documentation or reach out to the development team.


