class PipelineError(Exception):
    """Base class for exceptions in this pipeline."""
    def __init__(self, message: str, artifacts: dict = None):
        super().__init__(message)
        self.artifacts = artifacts

class ValidationError(PipelineError):
    """Raised when input data fails validation checks."""
    pass

class ClusterError(PipelineError):
    """Raised when clustering fails or produces invalid results."""
    pass

class DataLoadingError(PipelineError):
    """Raised when data loading steps fail."""
    pass

class PreprocessingError(PipelineError):
    """Raised when preprocessing steps fail."""
    pass

class ModelError(PipelineError):
    """Raised when model fitting or transformation fails."""
    pass