"""GPT Image 2 Polza MCP Server."""

__version__ = "0.6.0"
__author__ = "ivankhokholkov"
__description__ = "GPT Image 2 MCP server backed by Polza media and storage APIs"

from .server import create_app, create_wrapper_app, main

__all__ = ["create_app", "create_wrapper_app", "main"]
