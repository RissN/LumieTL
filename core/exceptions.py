"""Custom exception classes for LumieTL."""


class LumieTLError(Exception):
    """Base exception for all LumieTL errors."""


class TranslationError(LumieTLError):
    """Raised when image translation fails."""


class ModelNotFoundError(LumieTLError):
    """Raised when a required model file is missing."""


class ModelIntegrityError(LumieTLError):
    """Raised when a model file fails SHA256 verification."""


class UnsupportedEngineError(LumieTLError):
    """Raised when an unsupported translation engine is requested."""


class FileValidationError(LumieTLError):
    """Raised when an uploaded file fails validation."""


class RateLimitError(LumieTLError):
    """Raised when a rate limit is exceeded."""
