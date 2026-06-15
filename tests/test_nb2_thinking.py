import pytest

from gpt_image_2_polza_mcp_server.config.settings import Gemini31ImageConfig, ProImageConfig, ServerConfig
from gpt_image_2_polza_mcp_server.services.gemini_client import GeminiClient


def _build_client(model_config):
    return GeminiClient(ServerConfig(gemini_api_key="test-key"), model_config)


@pytest.mark.unit
def test_nb2_thinking_level_is_ignored_but_payload_building_still_works():
    client = _build_client(Gemini31ImageConfig())
    prompt, images = client._normalize_contents(["test prompt"])

    assert prompt == "test prompt"
    assert images == []
    assert client._filter_parameters({"thinking_level": "high"}) == {}


@pytest.mark.unit
def test_pro_thinking_level_is_still_ignored():
    client = _build_client(ProImageConfig())
    assert client._filter_parameters({"thinking_level": "high"}) == {}
