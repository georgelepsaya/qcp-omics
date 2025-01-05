from qcp_omics.mixins.analysis_mixin import AnalysisMixin
from qcp_omics.mixins.visualization_mixin import VisualizationMixin
from qcp_omics.models.omics_data import OmicsData
from qcp_omics.mixins.preprocessing_mixin import PreprocessingMixin
from qcp_omics.mixins.qc_mixin import QCMixin

class ProteomicsData(OmicsData, QCMixin, PreprocessingMixin, AnalysisMixin, VisualizationMixin):
    """
    Represents proteomics data, combining functionality for quality control,
    preprocessing, analysis, and visualization.

    Inherits from:
    - `OmicsData`: Base class for handling omics data.
    - `QCMixin`: Adds quality control functionality.
    - `PreprocessingMixin`: Adds preprocessing tools and methods.
    - `AnalysisMixin`: Adds data analysis functionality.
    - `VisualizationMixin`: Adds data visualization tools and methods.

    This class allows for custom implementations of functions in mixins, or new functions.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the ProteomicsData object. Passes all arguments to the `OmicsData` initializer.

        Args:
            *args: Positional arguments passed to the `OmicsData` initializer.
            **kwargs: Keyword arguments passed to the `OmicsData` initializer.
        """
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        """
        Provides a string representation of the ProteomicsData object for debugging and logging purposes.

        Returns:
            str: A string describing the ProteomicsData object.
        """
        return f"<ProteomicsData: {super().__repr__()}>"

