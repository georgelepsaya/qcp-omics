# QCP-Omics

![Tests are passing](https://github.com/georgelepsaya/qcp-omics/actions/workflows/tests.yaml/badge.svg)


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

# Metadata File Guide

## Overview

This guide explains how to create a metadata file required for running the tool in both interactive and metadata modes.

## Modes of Operation

### 1. Interactive Mode

**Command:**
```bash
qcp interactive
```

In this mode, users interactively input metadata through CLI prompts, except for data types (`dtypes`). The required JSON file must contain the `dtypes` field to specify the data types of dataset columns.

**Requirements:**
- Only the `dtypes` field is required. All other metadata will be collected during CLI interaction.
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

In this mode, the entire pipeline is executed automatically based on the provided metadata JSON file.

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
  "dataset_type": "clinical",
  "dataset_path": "data/clinical_data.csv",
  "metadata_path": "metadata.json",
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
    "age": "int",
    "death": "category",
    "bmi_num": "float"
  }
}
```

## Explanation of `steps_to_run`

### Full Pipeline (when `is_raw` is `true`)
All steps must be provided **in the exact order** listed below:

1. `identify_missing_values`
2. `handle_missing_values`
3. `handle_outliers` *(method required)*
    - Methods: *IQR*, *zscore*
5. `split_train_test`
6. `split_numerical_categorical`
7. `scale_numerical_features` *(method required)*
    - Methods: *standard_scaler*, *robust_scaler*
8. `transform_numerical_features` *(method required)*
    - Methods: *box-cox*, *log2*
9. `descriptive_statistics`
10. `pairwise_correlations_numerical` *(method required)*
    - Methods: *pearson*, *spearman*
11. `evaluate_distribution_features`
12. `dimensionality_reduction`

### Partial Pipeline (when `is_raw` is `false`)
Users can select any subset of steps but must maintain the **original order**. For example (imagine steps are numbered):

- Valid: `[3, 5, 6, 9]` → `handle_outliers`, `split_numerical_categorical`, `scale_numerical_features`, `pairwise_correlations_numerical`
- Invalid: `[3, 6, 5]` → `handle_outliers`, `scale_numerical_features`, `split_numerical_categorical` (Incorrect order)

## Output

- **Processed Data:**
  - `train_dataset.csv` and `test_dataset.csv` saved in `output_path`
- **Report:**
  - `report.html` saved in `report_path`

