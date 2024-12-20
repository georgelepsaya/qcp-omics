from qcp_omics.report_generation.report_step import report_step


class QCMixin:
    @report_step
    def step_qc(self):
        pass


