import pandas as pd
from qcp_omics.mixins.visualization_mixin import VisualizationMixin


def test_histograms_no_columns():
    df = pd.DataFrame()
    result = VisualizationMixin._histograms(df)
    assert "There are no columns" in result


def test_histograms_success():
    df = pd.DataFrame({
         "A": [1, 2, 3],
         "B": [4, 5, 6]
    })
    result = VisualizationMixin._histograms(df)
    assert "<div>" in result


def test_box_plots_no_outliers():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    result = VisualizationMixin._box_plots(df, [])
    assert "There are no outliers" in result


def test_box_plots_success():
    df = pd.DataFrame({"A": [1, 2, 3, 100], "B": [4, 5, 6, 7]})
    result = VisualizationMixin._box_plots(df, ["A"])
    assert "<div>" in result


def test_explained_variance():
    import numpy as np
    cum_var = np.array([10, 30, 60, 80, 95, 100])
    result = VisualizationMixin._explained_variance(cum_var)
    assert "<div>" in result


def test_pca_plot():
    df_pca = pd.DataFrame({
        "PC1": [1, 2, 3],
        "PC2": [4, 5, 6]
    })
    per_var = [50, 30]
    result = VisualizationMixin._pca_plot(df_pca, per_var)
    assert "<div>" in result


def test_heatmap():
    corr_df = pd.DataFrame({
        "A": [1, 0.5],
        "B": [0.5, 1]
    }, index=["A", "B"])
    result = VisualizationMixin._heatmap(corr_df)
    assert "<div>" in result
