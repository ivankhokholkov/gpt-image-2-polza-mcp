"""Fetch a previously-started Polza media generation by id.

Solves a common pain point: when the MCP client times out waiting for
`generate_image`, the generation on Polza's side is often already done.
This tool lets the client recover the result using the `gen_...` id
returned by Polza without re-running (and paying for) the generation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from pydantic import Field

from ..services import get_gemini_client, get_server_config


def register_fetch_generation_tool(server: FastMCP):
    """Register the fetch_generation tool with the FastMCP server."""

    @server.tool(
        annotations={
            "title": "Fetch a Polza media generation by id",
            "readOnlyHint": True,
            "openWorldHint": True,
        }
    )
    def fetch_generation(
        media_id: Annotated[
            str,
            Field(
                description=(
                    "Polza generation id (e.g. 'gen_2158264963618050049'). "
                    "Returned by the Polza API when an `images/generations` or "
                    "`/v1/media` call switches to async mode or when the MCP "
                    "client times out waiting for a synchronous response."
                ),
                min_length=4,
                max_length=128,
            ),
        ],
        output_path: Annotated[
            str | None,
            Field(
                description=(
                    "Where to save the downloaded asset(s). If a file path with "
                    "an extension is provided, saves the first asset there. If a "
                    "directory is provided, saves using '<media_id>_<index>.<ext>'. "
                    "If omitted, saves into IMAGE_OUTPUT_DIR."
                )
            ),
        ] = None,
        wait: Annotated[
            bool,
            Field(
                description=(
                    "If true (default), polls until the generation reports "
                    "'completed' or 'failed', respecting POLZA_POLL_TIMEOUT_SECONDS. "
                    "If false, returns the raw status without downloading."
                )
            ),
        ] = True,
    ) -> ToolResult:
        client = get_gemini_client()
        server_config = get_server_config()

        response = client.fetch_media_by_id(media_id, wait=wait)
        status = (response.get("status") or "").lower() if isinstance(response, dict) else ""

        if not wait and status not in {"completed", "failed"}:
            payload = {
                "media_id": media_id,
                "status": status or "unknown",
                "raw": response,
            }
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
            )

        # Extract URLs (reuse existing logic)
        urls = client._extract_output_urls(response)  # noqa: SLF001 — internal helper on our own client
        if not urls:
            raise RuntimeError(f"Generation {media_id} completed but returned no asset URLs")

        # Resolve output location
        base_dir = server_config.image_output_dir
        saved_paths: list[str] = []

        target_is_file = bool(output_path) and Path(output_path).suffix != ""
        if output_path and not target_is_file:
            Path(output_path).mkdir(parents=True, exist_ok=True)

        for idx, url in enumerate(urls):
            data = client.download_bytes(url)
            ext = _guess_ext_from_url(url)

            if target_is_file and idx == 0:
                dest = Path(output_path)
            elif output_path:
                dest = Path(output_path) / f"{media_id}_{idx}{ext}"
            else:
                dest = Path(base_dir) / f"{media_id}_{idx}{ext}"

            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            saved_paths.append(str(dest))

        payload = {
            "media_id": media_id,
            "status": status or "completed",
            "saved_paths": saved_paths,
            "source_urls": urls,
            "total_files": len(saved_paths),
        }
        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        )


def _guess_ext_from_url(url: str) -> str:
    # Polza returns direct S3 URLs ending with the file extension; fall back to .png.
    lowered = url.lower().split("?", 1)[0]
    for candidate in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".gif"):
        if lowered.endswith(candidate):
            return candidate if candidate != ".jpeg" else ".jpg"
    return os.path.splitext(lowered)[1] or ".png"
