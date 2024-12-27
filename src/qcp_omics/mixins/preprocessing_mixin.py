from qcp_omics.report_generation.report_step import report_step
import typing as t
from qcp_omics.utils.protocols import HasData


class PreprocessingMixin:
    @report_step(snapshot=True)
    def scale_features(self: HasData, method="standard_scaler"):
        pass

