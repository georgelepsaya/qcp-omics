from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar
from qcp_omics.utils.protocols import HasData
import plotly.express as px
import plotly.figure_factory as ff
import plotly.subplots as sp
import math


T = TypeVar("T", bound=HasData)


class VisualizationMixin:

    @staticmethod
    def _histograms(df):
        columns = df.columns
        rows = math.ceil(len(columns) / 5)

        fig = sp.make_subplots(rows=rows, cols=5, subplot_titles=columns)

        for i, col in enumerate(columns):
            dist = ff.create_distplot([df[col]], group_labels=[col])
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
    def _box_plots(df, columns):
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
    def _explained_variance(cum_var):
        fig = px.area(
            x=range(1, cum_var.shape[0] + 1),
            y=cum_var,
            labels={"x": "# Components", "y": "Explained Variance"}
        )
        return fig.to_html(full_html=False)


    @staticmethod
    def _pca_plot(df_pca, per_var):
        fig = px.scatter(df_pca,
                         x="PC1",
                         y="PC2",
                         height=800)
        return fig.to_html(full_html=False)


    @staticmethod
    def _heatmap(corr_df):
        fig = px.imshow(corr_df, width=800, height=800)
        return fig.to_html(full_html=False)
