# GPT Image 2 Polza MCP Server

This repository provides an MCP server for GPT Image 2 through Polza.

## Product identity

- Product: GPT Image 2 Polza MCP Server
- Provider: Polza
- Model ID: `openai/gpt-5.4-image-2`
- Public package: `gpt-image-2-polza-mcp-server`
- Python module: `gpt_image_2_polza_mcp_server`
- Default model tier: `gpt-image-2`

Do not describe this project as Nano Banana or as a Gemini MCP server. Some
legacy Gemini-compatible services remain in the implementation, but they are
not the product identity or the default route.

## Development

```bash
uv sync
uv run --extra test pytest -q
uv run gpt-image-2-polza-mcp-server
```

Authentication uses `POLZA_AI_API_KEY`. Do not add or require an OpenAI API key.
