from qcp_omics.analysis_mixin import AnalysisMixin
from qcp_omics.omics_data import OmicsData
from qcp_omics.preprocessing_mixin import PreprocessingMixin
from qcp_omics.qc_mixin import QCMixin


class GenomicsData(OmicsData, QCMixin, PreprocessingMixin, AnalysisMixin):
    pass