from qcp_omics.models.omics_data import OmicsData
from qcp_omics.report_generation.report_step import report_step
from qcp_omics.mixins.qc_mixin import QCMixin
from qcp_omics.mixins.preprocessing_mixin import PreprocessingMixin
from qcp_omics.mixins.analysis_mixin import AnalysisMixin
from qcp_omics.mixins.visualization_mixin import VisualizationMixin


class ClinicalData(OmicsData, QCMixin, PreprocessingMixin, AnalysisMixin, VisualizationMixin):
    @report_step
    def step_clinical(self):
        pass
