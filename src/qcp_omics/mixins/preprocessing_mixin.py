from qcp_omics.report_generation.report_step import report_step


class PreprocessingMixin:
    @report_step
    def step_preprocessing(self):
        pass

