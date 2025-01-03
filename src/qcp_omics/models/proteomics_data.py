from qcp_omics.mixins.analysis_mixin import AnalysisMixin
from qcp_omics.mixins.visualization_mixin import VisualizationMixin
from qcp_omics.models.omics_data import OmicsData
from qcp_omics.mixins.preprocessing_mixin import PreprocessingMixin
from qcp_omics.mixins.qc_mixin import QCMixin


class ProteomicsData(OmicsData, QCMixin, PreprocessingMixin, AnalysisMixin, VisualizationMixin):
    pass