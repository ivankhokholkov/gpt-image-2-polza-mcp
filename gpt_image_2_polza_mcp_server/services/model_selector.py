"""Intelligent model selection service for routing requests to optimal models."""

import logging

from ..config.settings import ModelSelectionConfig, ModelTier
from .image_service import ImageService
from .pro_image_service import ProImageService


class ModelSelector:
    """
    Intelligent model selection and routing service.

    Routes image generation/editing requests to the appropriate model
    (Flash or Pro) based on prompt analysis, explicit user preference,
    or automatic selection logic.
    """

    def __init__(
        self,
        flash_service: ImageService,
        pro_service: ProImageService,
        nb2_service: ProImageService,
        gpt_image_2_service: ProImageService,
        selection_config: ModelSelectionConfig,
    ):
        """
        Initialize model selector.

        Args:
            flash_service: Gemini 2.5 Flash Image service (speed-optimized)
            pro_service: Gemini 3 Pro Image service (quality-optimized)
            nb2_service: Gemini 3.1 Flash Image service (Flash speed + Pro quality)
            gpt_image_2_service: GPT Image 2 service (OpenAI via Polza)
            selection_config: Selection strategy configuration
        """
        self.flash_service = flash_service
        self.pro_service = pro_service
        self.nb2_service = nb2_service
        self.gpt_image_2_service = gpt_image_2_service
        self.config = selection_config
        self.logger = logging.getLogger(__name__)

    def select_model(
        self, prompt: str, requested_tier: ModelTier | None = None, **kwargs
    ) -> tuple[ImageService | ProImageService, ModelTier]:
        """
        Select appropriate model based on requirements.

        Args:
            prompt: User's image generation/edit prompt
            requested_tier: Explicit model tier request (or None for auto)
            **kwargs: Additional context (n, resolution, input_images, etc.)

        Returns:
            Tuple of (selected_service, selected_tier)
        """
        # Explicit selection takes precedence
        if requested_tier == ModelTier.FLASH:
            self.logger.info("Explicit Flash model selection")
            return self.flash_service, ModelTier.FLASH

        if requested_tier == ModelTier.PRO:
            self.logger.info("Explicit Pro model selection")
            return self.pro_service, ModelTier.PRO

        if requested_tier == ModelTier.NB2:
            self.logger.info("Explicit legacy Gemini 3.1 model selection")
            return self.nb2_service, ModelTier.NB2

        if requested_tier == ModelTier.GPT_IMAGE_2:
            self.logger.info("Explicit GPT Image 2 model selection")
            return self.gpt_image_2_service, ModelTier.GPT_IMAGE_2

        # This repository is dedicated to GPT Image 2.
        if requested_tier == ModelTier.AUTO or requested_tier is None:
            self.logger.info("Using GPT Image 2 as the default model")
            return self.gpt_image_2_service, ModelTier.GPT_IMAGE_2

        self.logger.warning(
            f"Unknown model tier '{requested_tier}', falling back to GPT Image 2"
        )
        return self.gpt_image_2_service, ModelTier.GPT_IMAGE_2

    def _auto_select(self, prompt: str, **kwargs) -> ModelTier:
        """
        Automatic model selection based on prompt and context analysis.

        Decision factors:
        1. Quality keywords in prompt (4k, professional, etc.)
        2. Speed keywords in prompt (quick, draft, etc.)
        3. Resolution requirements
        4. Multi-image conditioning
        5. Batch size

        Args:
            prompt: User's prompt text
            **kwargs: Additional context

        Returns:
            Selected ModelTier (FLASH or PRO)
        """
        quality_score = 0
        speed_score = 0

        prompt_lower = prompt.lower()

        # Analyze prompt for quality indicators
        quality_score = sum(
            1 for keyword in self.config.auto_quality_keywords if keyword in prompt_lower
        )

        # Analyze prompt for speed indicators
        speed_score = sum(
            1 for keyword in self.config.auto_speed_keywords if keyword in prompt_lower
        )

        # Strong quality indicators (weighted heavily)
        strong_quality_keywords = ["4k", "professional", "production", "high-res", "hd"]
        strong_quality_matches = sum(
            1 for keyword in strong_quality_keywords if keyword in prompt_lower
        )
        quality_score += strong_quality_matches * 2  # Double weight

        # Resolution parameter analysis
        # NB2 supports 4K natively, so resolution alone is not a PRO signal.
        # PRO is only favoured by strong quality keywords or thinking_level=high.

        # Batch size consideration
        n = kwargs.get("n", 1)
        if n > 2:
            # Multiple images favor speed
            speed_score += 1
            self.logger.debug(f"Multiple images requested (n={n}), favoring speed")

        # Multi-image conditioning
        input_images = kwargs.get("input_images")
        if input_images and len(input_images) > 1:
            # Pro model handles multi-image conditioning better
            quality_score += 1
            self.logger.debug(
                f"Multi-image conditioning ({len(input_images)} images), favoring quality"
            )

        # Thinking level hint — PRO-only feature, strong signal
        thinking_level = (kwargs.get("thinking_level") or "").lower()
        if thinking_level == "high":
            quality_score += 3
            self.logger.debug("thinking_level=high requested - favoring Pro model")

        # Note: enable_grounding no longer boosts Pro — NB2 also supports grounding

        # Decision logic
        self.logger.debug(
            f"Model selection scores - Quality: {quality_score}, Speed: {speed_score}"
        )

        if quality_score > speed_score:
            self.logger.info(
                f"Selected PRO model (quality_score={quality_score} > speed_score={speed_score})"
            )
            return ModelTier.PRO
        else:
            self.logger.info(
                f"Selected NB2 model (speed_score={speed_score} >= quality_score={quality_score})"
            )
            return ModelTier.NB2

    def get_model_info(self, tier: ModelTier) -> dict:
        """
        Get information about a specific model tier.

        Args:
            tier: Model tier to query

        Returns:
            Dictionary with model information
        """
        if tier == ModelTier.PRO:
            return {
                "tier": "pro",
                "name": "Gemini 3 Pro Image",
                "model_id": "gemini-3-pro-image-preview",
                "max_resolution": "4K (3840px)",
                "features": [
                    "4K resolution",
                    "Google Search grounding",
                    "Advanced reasoning",
                    "High-quality text rendering",
                ],
                "best_for": "Professional assets, production-ready images",
                "emoji": "🏆",
            }
        elif tier == ModelTier.NB2:
            return {
                "tier": "nb2",
                "name": "Gemini 3.1 Flash Image",
                "model_id": "gemini-3.1-flash-image-preview",
                "max_resolution": "4K (3840px)",
                "features": [
                    "Flash-speed generation",
                    "4K resolution",
                    "Google Search grounding",
                    "Subject consistency (5 chars, 14 objects)",
                    "Precision text rendering",
                ],
                "best_for": "Production images at Flash speed",
                "emoji": "🍌",
            }
        elif tier == ModelTier.GPT_IMAGE_2:
            return {
                "tier": "gpt-image-2",
                "name": "GPT Image 2",
                "model_id": "openai/gpt-5.4-image-2",
                "max_resolution": "4K (3840px)",
                "features": [
                    "OpenAI image model",
                    "4K resolution",
                    "High-quality composition",
                    "Strong text rendering",
                ],
                "best_for": "High-quality editorial and marketing visuals",
                "emoji": "🤖",
            }
        else:  # FLASH
            return {
                "tier": "flash",
                "name": "Gemini 2.5 Flash Image",
                "model_id": "gemini-2.5-flash-image",
                "max_resolution": "1024px",
                "features": ["Very fast generation", "Low latency", "High-volume support"],
                "best_for": "Rapid prototyping, quick iterations",
                "emoji": "⚡",
            }
