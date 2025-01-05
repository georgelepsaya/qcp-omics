from typing import TypeVar
import math
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.subplots as sp
from qcp_omics.utils.protocols import HasData

T = TypeVar("T", bound=HasData)

class VisualizationMixin:
    """
    A mixin class providing static methods for generating various visualizations using Plotly.
    """

    @staticmethod
    def _histograms(df: pd.DataFrame) -> str:
        """
        Generate histograms for all columns in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to visualize.

        Returns:
            str: An HTML string containing the histogram plots, or a message if the DataFrame is empty.
        """
        columns = df.columns

        if len(columns) == 0:
            return "<p>There are no columns in the forwarded dataset to generate histograms.</p>"

        rows = math.ceil(len(columns) / 5)

        fig = sp.make_subplots(rows=rows, cols=5, subplot_titles=columns)

        for i, col in enumerate(columns):
            dist = ff.create_distplot([df[col].dropna()], group_labels=[col])
            row_idx = i // 5 + 1
            col_idx = i % 5 + 1

            for trace in dist.data:
                fig.add_trace(trace, row=row_idx, col=col_idx)

        fig.update_layout(
            showlegend=False,
            height=300 * rows,
            width=1200
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def _box_plots(df: pd.DataFrame, columns: list[str]) -> str:
        """
        Generate box plots for specified columns in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to visualize.
            columns (list[str]): List of column names to generate box plots for.

        Returns:
            str: An HTML string containing the box plots, or a message if no columns are provided.
        """
        if len(columns) == 0:
            return "<p>There are no outliers</p>"

        rows = math.ceil(len(columns) / 5)

        fig = sp.make_subplots(rows=rows, cols=5, subplot_titles=columns)

        for i, col in enumerate(columns):
            box_fig = px.box(df, y=col)
            row_idx = i // 5 + 1
            col_idx = i % 5 + 1

            for trace in box_fig.data:
                fig.add_trace(trace, row=row_idx, col=col_idx)

        fig.update_layout(
            showlegend=False,
            height=300 * rows,
            width=1200
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def _explained_variance(cum_var: pd.Series) -> str:
        """
        Generate an area plot for explained variance.

        Args:
            cum_var (pd.Series): Cumulative variance explained by components.

        Returns:
            str: An HTML string containing the area plot.
        """
        fig = px.area(
            x=range(1, len(cum_var) + 1),
            y=cum_var,
            labels={"x": "# Components", "y": "Explained Variance"}
        )
        return fig.to_html(full_html=False)

    @staticmethod
    def _pca_plot(df_pca: pd.DataFrame, per_var: list[float]) -> str:
        """
        Generate a PCA scatter plot.

        Args:
            df_pca (pd.DataFrame): DataFrame containing PCA results with "PC1" and "PC2" columns.
            per_var (list[float]): Percentage variance explained by each component.

        Returns:
            str: An HTML string containing the PCA scatter plot.
        """
        fig = px.scatter(
            df_pca,
            x="PC1",
            y="PC2",
            labels={"PC1": f"PC1 ({per_var[0]:.2f}%)", "PC2": f"PC2 ({per_var[1]:.2f}%)"},
            height=800
        )
        return fig.to_html(full_html=False)

    @staticmethod
    def _heatmap(corr_df: pd.DataFrame) -> str:
        """
        Generate a heatmap for a correlation matrix.

        Args:
            corr_df (pd.DataFrame): Correlation matrix as a DataFrame.

        Returns:
            str: An HTML string containing the heatmap.
        """
        fig = px.imshow(corr_df, width=800, height=800)
        return fig.to_html(full_html=False)
