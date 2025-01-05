# QCP-Omics

![Tests](https://github.com/georgelepsaya/qcp-omics/actions/workflows/tests.yaml/badge.svg)


## Installation

### From PyPI

Requires Python version >= 3.11.

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install the tool: `pip install qcp-omics`
4. Verify installation: `qcp`

### Singularity (on HPC) - _recommended_
1. Load singularity: `module load singularity`
2. Pull the image from docker: `singularity pull qcp-omics.sif docker://georgelepsaya/qcp-omics:latest`
3. Verify installation: `singularity run qcp-omics.sif`

## Instructions

_will be added later_

```json
{
  "dataset_type": "clinical | genomics | proteomics",
  "dataset_path": "dataset/path.csv | .tsv",
  "metadata_path": "metadata/path",
  "output_path": "output/path",
  "features_cols": false,
  "en_header": true,
  "is_raw": true,
  "steps_to_run": ["step 1", "step 2"],
  "dtypes": {
    "feature1": "type",
    "feature2": "type"
  }
}
```
