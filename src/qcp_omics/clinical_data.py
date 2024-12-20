from qcp_omics.omics_data import OmicsData
from qcp_omics.report_generation.report_step import report_step
from .qc_mixin import QCMixin
from .preprocessing_mixin import PreprocessingMixin
from .analysis_mixin import AnalysisMixin
from .visualization_mixin import VisualizationMixin


class ClinicalData(OmicsData, QCMixin, PreprocessingMixin, AnalysisMixin, VisualizationMixin):
    @report_step
    def step_clinical(self):
        pass
