# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-04-22

### Added
- **`fetch_generation` tool**: recover a Polza media generation by its
  `gen_...` id — GETs `/v1/media/{id}`, optionally polls until the job is
  `completed`, downloads the asset(s) and saves them locally. This is the
  escape hatch for when the MCP client aborts `generate_image` on its own
  timeout while Polza is still finishing the job server-side, so users do
  not have to re-run (and re-pay for) the generation.
- **`GeminiClient.fetch_media_by_id` / `GeminiClient.download_bytes`**:
  public helpers for fetching and downloading media outside of the
  generation flow.

### Changed
- README rewritten in Russian.

## [0.5.1] - 2026-04-22

### Fixed
- **No duplicate image generations on retries**: identical requests now reuse the
  same upstream `media_id` instead of starting a new Polza generation when the
  previous one is still `pending` / `processing` or already `completed`.
- **Async-first Polza flow**: image generation now starts with `async: true`,
  then polls `GET /v1/media/{id}` instead of waiting for a long synchronous
  response that many MCP clients time out on.
- **Pending generation handoff**: `generate_image` now returns a structured
  pending response with `media_id` and explicit next-step guidance to poll via
  `fetch_generation`, so the agent does not blindly regenerate.
- **Forced rerun guardrail**: added `force_new_generation` for intentional
  reruns only, with a hard limit of 5 forced regenerations for the same request
  fingerprint before the server blocks more duplicates and requires explicit
  user confirmation.
- **Polling defaults**: aligned default poll interval with Polza guidance by
  moving from 2s to 3s.

### Added
- **Regression tests** for async timeout handoff, deduped generation reuse, and
  forced-rerun limits.

## [0.4.4] - 2026-03-27

### Fixed
- **NB2 thinking support**: Send `thinking_level` to Gemini as `thinking_config` for NB2 requests
- **NB2 aspect ratio validation**: Allow extreme aspect ratios (`4:1`, `1:4`, `8:1`, `1:8`) on the NB2 path
- **Runtime/test alignment**: Update tests to cover NB2 thinking and model-specific aspect ratio behavior

## [0.3.3] - 2026-01-26

### Added
- **aspect_ratio support for Pro model**: Pass aspect ratio parameter to Gemini API for Pro service (#10)
- **output_path support for Pro model**: Direct file saving with automatic thumbnail generation (#10)

### Fixed
- **Input validation**: Add aspect_ratio validation before API calls to prevent invalid requests
- **Error handling**: Graceful degradation when thumbnail creation fails (returns full image instead)
- **Code quality**: Fix datetime timezone awareness (DTZ005) and hashlib security parameter (S324)

### Contributors
- @paulrobello (#10)

## [0.3.2] - 2026-01-17

### Fixed
- **API compatibility**: Remove unsupported `output_mime_type` parameter from `ImageConfig` (#11)
- **Dependency version**: Bump `google-genai` requirement from `>=1.41.0` to `>=1.57.0` to ensure `image_size` parameter support (#12)
- **Test coverage**: Update test expectations after `output_mime_type` removal

### Changed
- `ImageConfig` is now only created when there are actual parameters to configure (aspect_ratio or resolution)

### Contributors
- @georgesung (#13)

## [0.3.1] - 2026-01-08

### Added
- **output_path parameter**: Control where generated images are saved (#8)
  - Exact file path mode: `/path/to/image.png`
  - Directory mode: `/path/to/dir/`
  - Default fallback: `IMAGE_OUTPUT_DIR` or `~/nanobanana-images`

### Fixed
- **Pro model routing**: Fix critical bug where Pro model requests were always routed to Flash service (#9)
- **API parameters**: Remove unsupported `thinking_level` parameter from gemini-3-pro-image-preview
- **Response modalities**: Change from `["Image"]` to `["TEXT", "IMAGE"]` for Pro model compatibility
- **Default region**: Change default GCP region to `global` for Pro model support

### Contributors
- @jgeewax
- @akshayvkt

## [0.3.0] - 2026-01-06

### Added
- **Nano Banana Pro Integration**: Support for Gemini 3 Pro Image model
  - 4K resolution support (up to 3840px)
  - Google Search grounding for factual accuracy
  - Configurable thinking levels (LOW/HIGH)
  - Media resolution control
- **Intelligent Model Selection**: Automatic routing between Flash and Pro models
  - `ModelSelector` service for smart model routing
  - Quality/speed keyword detection
  - Resolution-based selection
- **ADC Authentication**: Application Default Credentials support for Vertex AI (#6)

### Changed
- Multi-tier configuration system: `ModelSelectionConfig`, `ProImageConfig`
- `ProImageService` for dedicated Gemini 3 Pro Image operations

## [0.2.0] - 2026-01-03

### Added
- Initial production-ready release
- Gemini 2.5 Flash Image support
- FastMCP framework integration
- Image generation and editing tools
- Aspect ratio validation
- Comprehensive test coverage
- MIT License

[0.4.4]: https://github.com/zhongweili/nanobanana-mcp-server/compare/v0.4.3...v0.4.4
[0.3.3]: https://github.com/zhongweili/nanobanana-mcp-server/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/zhongweili/nanobanana-mcp-server/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/zhongweili/nanobanana-mcp-server/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/zhongweili/nanobanana-mcp-server/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zhongweili/nanobanana-mcp-server/releases/tag/v0.2.0
