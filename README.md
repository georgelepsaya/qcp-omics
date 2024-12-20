# QCP-Omics

## 1. Before you run the tool

### 1.1. Prepare metadata

1. Create a `metadata.json` file
2. If you plan to run the tool interactively, then only provide `"dtypes"` inside:

```json
{
  "dtypes": {
    "feature1": "type",
    "feature2": "type"
  }
}
```

Note:

- `"dtypes"` must represent data types for all of the columns/features of your dataset. In
case some of them are missing, a validation error will occur.
- If you choose interactive mode and still provide other fields in this file, they will be
ignored.

3. If you want to specify all you metadata then look at section 2.2.

## 2. Install and run the tool

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install the package manager: `pip install poetry`
4. Install all dependencies: `poetry install`
5. Ensure you can run the tool: `qcp`

### 2.1. Running with interactive input

If you want to run the tool by interactively providing information about your dataset then
simply run `qcp interactive` and answer the prompts.

### 2.2. Running with a prepared metadata.json file

If you wish to run the tool directly by providing all the input in a `metadata.json` file, then
make sure it contains all of the following fields:

```json
{
  "dataset_type": "clinical | genomics | proteomics",
  "dataset_path": "dataset/path",
  "metadata_path": "metadata/path",
  "output_path": "output/path",
  "features_cols": false,
  "en_header": true,
  "all_numeric": false,
  "is_raw": true,
  "steps_to_run": ["step 1", "step 2"],
  "dtypes": {
    "feature1": "type",
    "feature2": "type"
  }
}
```
