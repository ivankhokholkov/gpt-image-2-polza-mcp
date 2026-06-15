"""Custom exceptions for the GPT Image 2 Polza MCP Server."""

from dataclasses import dataclass
from typing import Any


class GptImage2Error(Exception):
    """Base exception class for GPT Image 2 MCP server errors."""

    pass


class ConfigurationError(GptImage2Error):
    """Raised when there's a configuration issue."""

    pass


class ValidationError(GptImage2Error):
    """Raised when input validation fails."""

    pass


class GeminiAPIError(GptImage2Error):
    """Raised when upstream media API calls fail."""

    pass


class ImageProcessingError(GptImage2Error):
    """Raised when image processing fails."""

    pass


class FileOperationError(GptImage2Error):
    """Raised when file operations fail."""

    pass


class AuthenticationError(GptImage2Error):
    """Base exception for authentication errors."""

    pass


class ADCConfigurationError(AuthenticationError):
    """Raised when an unsupported legacy authentication mode is requested."""

    pass


@dataclass
class AsyncGenerationPending(GptImage2Error):
    """Raised when a generation is still running and should be polled, not restarted."""

    media_id: str
    status: str
    response: dict[str, Any]

    def __str__(self) -> str:
        return f"Generation {self.media_id} is still {self.status}"
