from qcp_omics.report_generation.report_step import report_step
from typing import TypeVar
from qcp_omics.utils.protocols import HasData
import plotly.express as px


T = TypeVar("T", bound=HasData)


class VisualizationMixin:

    def histogram(self: T):
        pass


    def box_plot(self: T):
        pass


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
