from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv

from .constants import AUTH_ERROR_MESSAGES


class ModelTier(str, Enum):
    """Model selection options."""

    FLASH = "flash"  # Speed-optimized (Gemini 2.5 Flash)
    PRO = "pro"  # Quality-optimized (Gemini 3 Pro)
    NB2 = "nb2"  # Legacy Gemini 3.1 Flash Image tier
    GPT_IMAGE_2 = "gpt-image-2"  # GPT Image 2 (OpenAI via Polza)
    AUTO = "auto"  # Automatic selection


class AuthMethod(Enum):
    """Authentication method options."""

    API_KEY = "api_key"
    VERTEX_AI = "vertex_ai"
    AUTO = "auto"


class ThinkingLevel(str, Enum):
    """Reasoning level hints for model selection."""

    LOW = "low"  # Minimal latency, less reasoning
    HIGH = "high"  # Maximum reasoning (default for Pro)


class MediaResolution(str, Enum):
    """Media resolution for vision processing."""

    LOW = "low"  # Faster, less detail
    MEDIUM = "medium"  # Balanced
    HIGH = "high"  # Maximum detail


@dataclass
class ServerConfig:
    """Server configuration settings."""

    gemini_api_key: str | None = None
    server_name: str = "gpt-image-2-polza-mcp-server"
    transport: str = "stdio"  # stdio or http
    host: str = "127.0.0.1"
    port: int = 9000
    mask_error_details: bool = False
    max_concurrent_requests: int = 10
    image_output_dir: str = ""
    return_full_image: bool = False
    auth_method: AuthMethod = AuthMethod.AUTO
    gcp_project_id: str | None = None
    gcp_region: str = "us-central1"
    gemini_base_url: str | None = None
    polza_poll_interval_seconds: float = 3.0
    polza_poll_timeout_seconds: int = 120
    polza_sync_wait_seconds: int = 45
    polza_generation_cache_ttl_seconds: int = 900
    polza_max_forced_regenerations: int = 5
    polza_external_user_id: str | None = None

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        # Auth method
        auth_method_str = os.getenv("GPT_IMAGE_AUTH_METHOD", "auto").lower()
        try:
            auth_method = AuthMethod(auth_method_str)
        except ValueError:
            auth_method = AuthMethod.AUTO

        api_key = (
            os.getenv("POLZA_AI_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        gcp_project = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        gcp_region = os.getenv("GCP_REGION") or os.getenv("GOOGLE_CLOUD_LOCATION") or "global"

        if auth_method == AuthMethod.API_KEY:
            if not api_key:
                raise ValueError(AUTH_ERROR_MESSAGES["api_key_required"])

        elif auth_method == AuthMethod.VERTEX_AI:
            raise ValueError(AUTH_ERROR_MESSAGES["vertex_ai_project_required"])

        else:
            if not api_key:
                raise ValueError(AUTH_ERROR_MESSAGES["no_auth_configured"])
            auth_method = AuthMethod.API_KEY

        output_dir = os.getenv("IMAGE_OUTPUT_DIR", "").strip()
        if not output_dir:
            output_dir = str(Path.home() / "gpt-image-2-images")

        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        gemini_base_url = (
            os.getenv("POLZA_BASE_URL")
            or os.getenv("GEMINI_BASE_URL")
            or "https://polza.ai/api"
        )
        gemini_base_url = gemini_base_url.strip() or "https://polza.ai/api"

        return cls(
            gemini_api_key=api_key,
            auth_method=auth_method,
            gcp_project_id=gcp_project,
            gcp_region=gcp_region,
            gemini_base_url=gemini_base_url,
            polza_poll_interval_seconds=float(os.getenv("POLZA_POLL_INTERVAL_SECONDS", "3")),
            polza_poll_timeout_seconds=int(os.getenv("POLZA_POLL_TIMEOUT_SECONDS", "120")),
            polza_sync_wait_seconds=int(os.getenv("POLZA_SYNC_WAIT_SECONDS", "45")),
            polza_generation_cache_ttl_seconds=int(
                os.getenv("POLZA_GENERATION_CACHE_TTL_SECONDS", "900")
            ),
            polza_max_forced_regenerations=int(
                os.getenv("POLZA_MAX_FORCED_REGENERATIONS", "5")
            ),
            polza_external_user_id=os.getenv("POLZA_EXTERNAL_USER_ID") or None,
            transport=os.getenv("FASTMCP_TRANSPORT", "stdio"),
            host=os.getenv("FASTMCP_HOST", "127.0.0.1"),
            port=int(os.getenv("FASTMCP_PORT", "9000")),
            mask_error_details=os.getenv("FASTMCP_MASK_ERRORS", "false").lower() == "true",
            image_output_dir=str(output_path),
            return_full_image=os.getenv("RETURN_FULL_IMAGE", "false").strip().lower()
            in ("true", "1", "yes"),
        )


@dataclass
class BaseModelConfig:
    """Shared base configuration for all models."""

    max_images_per_request: int = 4
    max_inline_image_size: int = 20 * 1024 * 1024  # 20MB
    default_image_format: str = "png"
    request_timeout: int = 60  # seconds


@dataclass
class FlashImageConfig(BaseModelConfig):
    """Gemini 2.5 Flash Image configuration (speed-optimized)."""

    model_name: str = "gemini-2.5-flash-image"
    max_resolution: int = 1024
    supports_thinking: bool = False
    supports_grounding: bool = False
    supports_media_resolution: bool = False


@dataclass
class ProImageConfig(BaseModelConfig):
    """Gemini 3 Pro Image configuration (quality-optimized)."""

    model_name: str = "gemini-3-pro-image-preview"
    max_resolution: int = 3840  # 4K
    default_resolution: str = "high"  # low/medium/high
    default_thinking_level: ThinkingLevel = ThinkingLevel.HIGH
    default_media_resolution: MediaResolution = MediaResolution.HIGH
    supports_thinking: bool = False
    supports_grounding: bool = True
    supports_media_resolution: bool = True
    supports_extreme_aspect_ratios: bool = False
    enable_search_grounding: bool = True
    request_timeout: int = 90  # Pro model needs more time for 4K


@dataclass
class Gemini31ImageConfig(ProImageConfig):
    """Legacy Gemini 3.1 Flash Image configuration."""

    model_name: str = "gemini-3.1-flash-image-preview"
    request_timeout: int = 60  # Flash-speed model
    supports_thinking: bool = True  # Supports Minimal/High/Dynamic thinking
    supports_extreme_aspect_ratios: bool = False


@dataclass
class GptImage2Config(BaseModelConfig):
    """GPT Image 2 configuration (OpenAI via Polza)."""

    model_name: str = "openai/gpt-5.4-image-2"
    max_resolution: int = 3840  # 4K
    default_resolution: str = "high"
    default_thinking_level: ThinkingLevel = ThinkingLevel.HIGH
    default_media_resolution: MediaResolution = MediaResolution.HIGH
    supports_thinking: bool = False
    supports_grounding: bool = False
    supports_media_resolution: bool = True
    supports_extreme_aspect_ratios: bool = False
    enable_search_grounding: bool = False
    request_timeout: int = 90


@dataclass
class ModelSelectionConfig:
    """Configuration for intelligent model selection."""

    default_tier: ModelTier = ModelTier.GPT_IMAGE_2
    auto_quality_keywords: list[str] = field(
        default_factory=lambda: [
            "4k",
            "high quality",
            "professional",
            "production",
            "high-res",
            "high resolution",
            "detailed",
            "sharp",
            "crisp",
            "hd",
            "ultra",
            "premium",
            "magazine",
            "print",
        ]
    )
    auto_speed_keywords: list[str] = field(
        default_factory=lambda: [
            "quick",
            "fast",
            "draft",
            "prototype",
            "sketch",
            "rapid",
            "rough",
            "temporary",
            "test",
        ]
    )

    @classmethod
    def from_env(cls) -> "ModelSelectionConfig":
        """Load model selection config from environment."""
        load_dotenv()

        model_tier_str = os.getenv("GPT_IMAGE_MODEL", "gpt-image-2").lower()
        try:
            default_tier = ModelTier(model_tier_str)
        except ValueError:
            default_tier = ModelTier.GPT_IMAGE_2

        return cls(default_tier=default_tier)


@dataclass
class GeminiConfig:
    """Legacy Gemini API configuration (backward compatibility)."""

    model_name: str = "gemini-2.5-flash-image"
    max_images_per_request: int = 4
    max_inline_image_size: int = 20 * 1024 * 1024  # 20MB
    default_image_format: str = "png"
    request_timeout: int = 60  # seconds - increased for image generation
