import os
import pytest
from unittest.mock import patch

from gpt_image_2_polza_mcp_server.config.settings import ServerConfig, AuthMethod, GeminiConfig
from gpt_image_2_polza_mcp_server.services.gemini_client import GeminiClient


class TestAuthConfiguration:
    def test_api_key_auth_requires_api_key(self):
        """API key is required when using api_key auth method."""
        # Ensure no API key is set - also mock load_dotenv to prevent .env loading
        with patch("gpt_image_2_polza_mcp_server.config.settings.load_dotenv"):
            with patch.dict(os.environ, {"GPT_IMAGE_AUTH_METHOD": "api_key"}, clear=True):
                with pytest.raises(ValueError):
                    ServerConfig.from_env()

    def test_vertex_ai_auth_is_rejected(self):
        """Vertex auth is not supported in the Polza adapter."""
        with patch("gpt_image_2_polza_mcp_server.config.settings.load_dotenv"):
            with patch.dict(os.environ, {"GPT_IMAGE_AUTH_METHOD": "vertex_ai"}, clear=True):
                with pytest.raises(ValueError):
                    ServerConfig.from_env()

    def test_auto_selects_api_key_when_available(self):
        """Auto mode selects api_key when POLZA_AI_API_KEY is available."""
        with patch("gpt_image_2_polza_mcp_server.config.settings.load_dotenv"):
            with patch.dict(os.environ, {"POLZA_AI_API_KEY": "test-key"}, clear=True):
                config = ServerConfig.from_env()
                assert config.auth_method == AuthMethod.API_KEY

    def test_auto_fails_when_no_auth_configured(self):
        """Auto mode raises error when no auth credentials are configured."""
        with patch("gpt_image_2_polza_mcp_server.config.settings.load_dotenv"):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError):
                    ServerConfig.from_env()

    def test_polza_base_url_whitespace_uses_default(self):
        """Whitespace-only POLZA_BASE_URL should fall back to the default URL."""
        with patch("gpt_image_2_polza_mcp_server.config.settings.load_dotenv"):
            with patch.dict(
                os.environ,
                {
                    "POLZA_AI_API_KEY": "test-key",
                    "POLZA_BASE_URL": "   ",
                },
                clear=True,
            ):
                config = ServerConfig.from_env()
                assert config.gemini_base_url == "https://polza.ai/api"


class TestGeminiClientAuth:
    def test_api_key_client_creation(self):
        """Client is created correctly with Polza API key authentication."""
        config = ServerConfig(gemini_api_key="test-key", auth_method=AuthMethod.API_KEY)
        gemini_config = GeminiConfig()
        client = GeminiClient(config, gemini_config)
        assert client.base_url == "https://polza.ai/api"

    def test_api_key_client_creation_with_base_url_uses_custom_url(self):
        """Custom base URL should be stored on the client."""
        config = ServerConfig(
            gemini_api_key="test-key",
            auth_method=AuthMethod.API_KEY,
            gemini_base_url="https://proxy.example.com/api?token=secret",
        )
        gemini_config = GeminiConfig()
        client = GeminiClient(config, gemini_config)
        assert client.base_url == "https://proxy.example.com/api?token=secret"
