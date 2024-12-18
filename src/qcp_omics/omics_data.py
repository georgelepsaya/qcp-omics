from abc import ABC
import pandas as pd

class OmicsData(ABC):
    def __init__(self, metadata: dict) -> None:
        self.metadata = metadata

    def load_data(self) -> pd.DataFrame:
        dataset_path = self.metadata["dataset_path"]
        dataset_sep = self.metadata["dataset_sep"]
        df = pd.read_table(dataset_path, sep=dataset_sep, index_col=0)
        return df

    def execute_steps(self) -> None:
        steps: list[str] = self.metadata["steps"]
        for step in steps:
            match step:
                case "identify_missing_values":
                    pass
                case "detect_outliers":
                    pass
                case "handle_missing_values":
                    pass
                case "handle_outliers":
                    pass
                case "normalize_numerical_features":
                    pass
                case "transform":
                    pass
                case "encode_categorical_variables":
                    pass
                case "scale_features":
                    pass
                case "dimensionality_reduction":
                    pass
                case "distribution_numerical":
                    pass
                case "distribution_categorical":
                    pass
                case "visualize_outliers":
                    pass
                case "correlation_heatmaps":
                    pass
                case "correlation_heatmaps":
                    pass
                case "feature_interdependencies":
                    pass
                case "categorical_feature_relationships":
                    pass
                case "visualize_dimensionality_reduction":
                    pass
                case "descriptive_statistics":
                    pass
                case "group_comparisons":
                    pass
                case "correlation_coefficients":
                    pass
                case "multicollinearity":
                    pass
                case "build_models":
                    pass
                case "evaluate_model_performance":
                    pass
                case "feature_importance_analysis":
                    pass
                case "hypothesis_testing":
                    pass


