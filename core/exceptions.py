"""LumieTL Custom Exceptions."""


class LumieTLError(Exception):
    """Base exception for all LumieTL errors."""


class TranslationError(LumieTLError):
    """Raised when an error occurs during the translation pipeline."""


class ModelNotFoundError(LumieTLError):
    """Raised when required ONNX models are missing."""


class ModelIntegrityError(LumieTLError):
    """Raised when downloaded model checksum does not match expected value."""


class UnsupportedEngineError(LumieTLError):
    """Raised when an unsupported translation engine is requested."""


class FileValidationError(LumieTLError):
    """Raised when an input image file fails security or format validation."""


class RateLimitError(LumieTLError):
    """Raised when rate limits are exceeded."""


class SecurityError(LumieTLError):
    """Raised on security violation (path traversal, corrupted secret, etc.)."""
