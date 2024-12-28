from qcp_omics.report_generation.report_step import report_step


class VisualizationMixin:
    @report_step()
    def vis(self):
        pass

