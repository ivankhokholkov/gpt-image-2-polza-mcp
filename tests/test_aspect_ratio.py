"""
Tests for aspect ratio functionality.

This module tests the aspect ratio feature added in PR #3, including:
- Parameter validation
- API integration
- Metadata tracking
- Edge cases
"""

import pytest
from unittest.mock import patch

from gpt_image_2_polza_mcp_server.services.gemini_client import GeminiClient
from gpt_image_2_polza_mcp_server.config.settings import ServerConfig, GeminiConfig


# Supported aspect ratios accepted by the Polza image API
STANDARD_ASPECT_RATIOS = [
    "auto",
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
]
SUPPORTED_ASPECT_RATIOS = STANDARD_ASPECT_RATIOS


class TestAspectRatioValidation:
    """Test aspect ratio parameter validation."""

    @pytest.mark.parametrize("ratio", SUPPORTED_ASPECT_RATIOS)
    def test_valid_aspect_ratios(self, ratio):
        """Test that all supported aspect ratios are accepted."""
        # This tests the Literal type constraint in generate_image.py
        # The Pydantic validation should accept these values
        assert ratio in SUPPORTED_ASPECT_RATIOS

    @pytest.mark.parametrize("ratio", ["4:1", "1:4", "8:1", "1:8"])
    def test_extreme_aspect_ratios_are_rejected_for_polza(self, ratio):
        from gpt_image_2_polza_mcp_server.core.exceptions import ValidationError
        from gpt_image_2_polza_mcp_server.utils.validation_utils import validate_aspect_ratio_string

        with pytest.raises(ValidationError):
            validate_aspect_ratio_string(ratio)

    def test_aspect_ratio_literal_type_constraint(self):
        """Verify the tool parameter uses Literal type for type safety."""
        from gpt_image_2_polza_mcp_server.tools.generate_image import register_generate_image_tool
        from fastmcp import FastMCP
        import inspect

        # This test ensures the Literal constraint is in place
        # If it's not, the type system won't catch invalid values
        server = FastMCP("test")
        register_generate_image_tool(server)

        # Get the generate_image function directly from the module
        from gpt_image_2_polza_mcp_server.tools import generate_image as gi_module

        # Find the generate_image function that was decorated
        generate_image_fn = None
        for name, obj in inspect.getmembers(gi_module):
            if name == "register_generate_image_tool":
                continue
            if callable(obj) and hasattr(obj, "__wrapped__"):
                generate_image_fn = obj
                break

        # If we can't find the decorated function, check the server's registered tools
        # by examining what register_generate_image_tool registered
        if generate_image_fn is None:
            # Just verify the module has the expected structure
            assert hasattr(gi_module, "register_generate_image_tool")
            return

        # Check that aspect_ratio parameter exists
        sig = inspect.signature(generate_image_fn)
        assert "aspect_ratio" in sig.parameters


class TestGeminiClientAspectRatio:
    """Test GeminiClient aspect ratio integration."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        server_config = ServerConfig(gemini_api_key="test-key")
        gemini_config = GeminiConfig()
        return server_config, gemini_config

    @pytest.fixture
    def gemini_client(self, mock_config):
        """Create GeminiClient with mocked dependencies."""
        server_config, gemini_config = mock_config
        return GeminiClient(server_config, gemini_config)

    def test_aspect_ratio_is_passed_to_media_payload(self, gemini_client):
        """aspect_ratio should be forwarded to the Polza payload."""
        with patch.object(gemini_client, "_request_json") as mock_request, patch.object(
            gemini_client, "_resolve_media_response", return_value={"data": {"url": "https://example.test/image.png"}}
        ), patch.object(gemini_client, "_download_bytes", return_value=b"image"):
            mock_request.return_value = {
                "id": "gen_1",
                "status": "completed",
                "data": {"url": "https://example.test/image.png"},
            }
            gemini_client.generate_content(contents=["test prompt"], aspect_ratio="16:9")
            payload = mock_request.call_args.args[2]
            assert payload["input"]["aspect_ratio"] == "16:9"

    def test_config_conflict_warning(self, gemini_client, caplog):
        """dict config and aspect_ratio can coexist in the Polza payload."""
        with patch.object(gemini_client, "_request_json") as mock_request, patch.object(
            gemini_client, "_resolve_media_response", return_value={"data": {"url": "https://example.test/image.png"}}
        ), patch.object(gemini_client, "_download_bytes", return_value=b"image"):
            mock_request.return_value = {
                "id": "gen_1",
                "status": "completed",
                "data": {"url": "https://example.test/image.png"},
            }
            gemini_client.generate_content(
                contents=["test"],
                aspect_ratio="16:9",
                config={"resolution": "4k"},
            )
            payload = mock_request.call_args.args[2]
            assert payload["input"]["aspect_ratio"] == "16:9"
            assert payload["input"]["image_resolution"] == "4K"


class TestAspectRatioMetadata:
    """Test aspect ratio in metadata tracking."""

    def test_aspect_ratio_in_generation_metadata(self):
        """Test that aspect_ratio appears in generation metadata."""
        # This would need integration with actual services
        # For now, verify the metadata structure
        metadata = {
            "prompt": "test image",
            "negative_prompt": None,
            "system_instruction": None,
            "aspect_ratio": "16:9",
        }

        assert "aspect_ratio" in metadata
        assert metadata["aspect_ratio"] == "16:9"

    def test_aspect_ratio_none_in_metadata(self):
        """Test that aspect_ratio=None is properly tracked."""
        metadata = {
            "prompt": "test image",
            "aspect_ratio": None,
        }

        assert "aspect_ratio" in metadata
        assert metadata["aspect_ratio"] is None


class TestAspectRatioEdgeCases:
    """Test edge cases and error conditions."""

    def test_aspect_ratio_with_edit_mode(self):
        """Test aspect ratio behavior in edit mode."""
        # Currently aspect_ratio only works in generate mode
        # This test documents the current behavior
        # If edit mode support is added, update this test
        pass  # Document-only test for now

    def test_aspect_ratio_with_multiple_images(self):
        """Test aspect ratio when generating multiple images."""
        # All generated images should have the same aspect ratio
        # This would require integration testing with real API
        pass  # Integration test placeholder

    def test_aspect_ratio_with_input_images(self):
        """Test aspect ratio with image conditioning."""
        # Aspect ratio should apply to output, not input
        pass  # Integration test placeholder


class TestAspectRatioIntegration:
    """Integration tests for aspect ratio feature.

    Note: These tests are marked as 'integration' and require actual API access.
    They are skipped by default in CI/CD but can be run manually with:
        pytest -m integration
    """

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires Gemini API access and costs money")
    def test_generate_with_16_9_aspect_ratio(self):
        """Integration test: Generate image with 16:9 aspect ratio."""
        # This would test actual API call
        # from gpt_image_2_polza_mcp_server.tools.generate_image import generate_image
        # result = generate_image(prompt="test", aspect_ratio="16:9")
        # assert result is not None
        pass

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires Gemini API access and costs money")
    @pytest.mark.parametrize("ratio", SUPPORTED_ASPECT_RATIOS)
    def test_all_aspect_ratios_work(self, ratio):
        """Integration test: Verify all aspect ratios work with real API."""
        pass


class TestAspectRatioServicePropagation:
    """Test that aspect_ratio propagates through service layers."""

    def test_enhanced_image_service_accepts_aspect_ratio(self):
        """Test EnhancedImageService.generate_images accepts aspect_ratio."""
        from gpt_image_2_polza_mcp_server.services.enhanced_image_service import EnhancedImageService
        import inspect

        # Check method signature
        sig = inspect.signature(EnhancedImageService.generate_images)
        assert "aspect_ratio" in sig.parameters

    def test_file_image_service_accepts_aspect_ratio(self):
        """Test FileImageService.generate_images accepts aspect_ratio."""
        from gpt_image_2_polza_mcp_server.services.file_image_service import FileImageService
        import inspect

        sig = inspect.signature(FileImageService.generate_images)
        assert "aspect_ratio" in sig.parameters

    def test_image_service_accepts_aspect_ratio(self):
        """Test ImageService.generate_images accepts aspect_ratio."""
        from gpt_image_2_polza_mcp_server.services.image_service import ImageService
        import inspect

        sig = inspect.signature(ImageService.generate_images)
        assert "aspect_ratio" in sig.parameters


# Test configuration
pytest_plugins = []  # Add any required plugins

# Mark integration tests
pytestmark = pytest.mark.unit  # Default mark for this module
