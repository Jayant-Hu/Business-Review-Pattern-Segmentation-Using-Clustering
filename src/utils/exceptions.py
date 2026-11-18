"""
Custom domain-specific exceptions for UrbanPulse AI.
"""

class UrbanPulseException(Exception):
    """Base exception for all UrbanPulse domain errors."""
    pass

class DataLoadingError(UrbanPulseException):
    """Raised when raw or processed data cannot be located or loaded."""
    pass

class DataValidationError(UrbanPulseException):
    """Raised when dataset schemas or required features fail validation."""
    pass

class ModelExecutionError(UrbanPulseException):
    """Raised when model training, prediction, or pipeline artifact loading fails."""
    pass

class GeocodingError(UrbanPulseException):
    """Raised when geocoding service encounters a critical failure."""
    pass
