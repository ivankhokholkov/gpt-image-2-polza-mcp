from unittest.mock import patch

import pytest

from gpt_image_2_polza_mcp_server.config.settings import GeminiConfig, ServerConfig
from gpt_image_2_polza_mcp_server.core.exceptions import AsyncGenerationPending, ValidationError
from gpt_image_2_polza_mcp_server.services.gemini_client import GeminiClient


@pytest.fixture
def gemini_client():
    GeminiClient._generation_cache.clear()
    server_config = ServerConfig(
        gemini_api_key="test-key",
        polza_poll_interval_seconds=0.01,
        polza_poll_timeout_seconds=1,
        polza_sync_wait_seconds=0.02,
        polza_generation_cache_ttl_seconds=60,
        polza_max_forced_regenerations=5,
    )
    client = GeminiClient(server_config, GeminiConfig())
    yield client
    GeminiClient._generation_cache.clear()


def test_generate_content_reuses_existing_generation_instead_of_posting_again(gemini_client):
    post_response = {"id": "gen_1", "status": "pending"}
    completed_response = {
        "id": "gen_1",
        "status": "completed",
        "data": {"url": "https://example.test/image.png"},
    }

    with patch.object(gemini_client, "_request_json") as mock_request, patch.object(
        gemini_client, "_download_bytes", return_value=b"image"
    ):
        mock_request.side_effect = [
            post_response,
            completed_response,
            completed_response,
        ]

        first = gemini_client.generate_content(["same prompt"])
        second = gemini_client.generate_content(["same prompt"])

        assert first.generated_images == [b"image"]
        assert second.generated_images == [b"image"]
        post_calls = [call for call in mock_request.call_args_list if call.args[:2] == ("POST", "/v1/media")]
        assert len(post_calls) == 1


def test_generate_content_raises_pending_with_media_id_when_sync_window_expires(gemini_client):
    pending_response = {"id": "gen_2", "status": "pending"}

    with patch.object(
        gemini_client,
        "_request_json",
        side_effect=[pending_response, pending_response, pending_response, pending_response],
    ):
        with pytest.raises(AsyncGenerationPending) as exc_info:
            gemini_client.generate_content(["slow prompt"])

    assert exc_info.value.media_id == "gen_2"
    assert exc_info.value.status == "pending"


def test_force_new_generation_limit_requires_explicit_user_confirmation(gemini_client):
    gemini_client.config.polza_max_forced_regenerations = 2

    with patch.object(
        gemini_client,
        "_request_json",
        return_value={
            "id": "gen_done",
            "status": "completed",
            "data": {"url": "https://example.test/image.png"},
        },
    ), patch.object(gemini_client, "_download_bytes", return_value=b"image"):
        gemini_client.generate_content(["same prompt"], force_new_generation=True)
        gemini_client.generate_content(["same prompt"], force_new_generation=True)

        with pytest.raises(ValidationError):
            gemini_client.generate_content(["same prompt"], force_new_generation=True)
