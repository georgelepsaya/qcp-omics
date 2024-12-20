from qcp_omics.report_generation.report_step import report_step


class AnalysisMixin:
    @report_step
    def step_analysis(self):
        pass

