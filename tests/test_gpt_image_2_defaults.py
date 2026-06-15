from unittest.mock import patch

from gpt_image_2_polza_mcp_server.config.settings import ModelSelectionConfig, ModelTier
from gpt_image_2_polza_mcp_server.services.model_selector import ModelSelector


def test_model_selection_config_defaults_to_gpt_image_2():
    with patch(
        "gpt_image_2_polza_mcp_server.config.settings.load_dotenv"
    ), patch.dict("os.environ", {}, clear=True):
        config = ModelSelectionConfig.from_env()

    assert config.default_tier == ModelTier.GPT_IMAGE_2


def test_auto_selection_routes_to_gpt_image_2():
    flash_service = object()
    pro_service = object()
    legacy_gemini_service = object()
    gpt_image_2_service = object()
    selector = ModelSelector(
        flash_service=flash_service,
        pro_service=pro_service,
        nb2_service=legacy_gemini_service,
        gpt_image_2_service=gpt_image_2_service,
        selection_config=ModelSelectionConfig(),
    )

    service, tier = selector.select_model("Create an editorial image", ModelTier.AUTO)

    assert service is gpt_image_2_service
    assert tier == ModelTier.GPT_IMAGE_2
