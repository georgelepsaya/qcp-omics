from qcp_omics.analysis_mixin import AnalysisMixin
from qcp_omics.omics_data import OmicsData
from qcp_omics.preprocessing_mixin import PreprocessingMixin
from qcp_omics.qc_mixin import QCMixin


class ClinicalData(OmicsData, QCMixin, PreprocessingMixin, AnalysisMixin):
    def step_clinical(self):
        pass
