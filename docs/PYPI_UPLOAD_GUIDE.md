# PyPI Upload Guide for Nano Banana MCP Server

This guide will help you upload your MCP server to PyPI so users can install it with `uvx`.

## Prerequisites

1. **PyPI Account**: Create accounts on both [TestPyPI](https://test.pypi.org/) and [PyPI](https://pypi.org/)
2. **API Tokens**: Generate API tokens for secure uploads
3. **Build Tools**: Install required build tools

## Step 1: Install Build Dependencies

```bash
# Install build dependencies with uv
uv add --dev build twine

# Or if you want to install globally
uvx install build twine
```

## Step 2: Build the Package

```bash
# Run the build script
uv run python scripts/build.py

# Or manually:
uv run python -m build
```

This will create:
- `dist/nanobanana-mcp-server-0.1.0.tar.gz` (source distribution)
- `dist/gpt_image_2_polza_mcp_server-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test Upload to TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
uv run python scripts/upload.py
# Choose option 1 for TestPyPI

# Or manually:
uv run twine upload --repository testpypi dist/*
```

## Step 4: Test Installation from TestPyPI

```bash
# Test installation with uvx
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nanobanana-mcp-server

# Test the command works
nanobanana-mcp-server --help
```

## Step 5: Upload to Production PyPI

Once testing is successful:

```bash
# Upload to production PyPI
uv run python scripts/upload.py
# Choose option 2 for PyPI

# Or manually:
uv run twine upload dist/*
```

## Step 6: Test Final Installation

```bash
# Test installation from PyPI
uvx nanobanana-mcp-server

# Or with pip
pip install nanobanana-mcp-server
```

## Usage After Installation

After successful upload, users can install and run your server with:

```bash
# Install and run with uvx (recommended)
uvx nanobanana-mcp-server

# Or install globally
pip install nanobanana-mcp-server
nanobanana-mcp-server

# Or shorter command
nanobanana-mcp
```

## FastMCP Integration

Your server will also be available as a FastMCP entry point:

```bash
# Users can run with FastMCP CLI
fastmcp run nanobanana-mcp-server

# Or in development mode
fastmcp dev nanobanana-mcp-server
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are listed in `pyproject.toml`
2. **Entry Point Issues**: Verify the console scripts point to the correct module paths
3. **Version Conflicts**: Check for version conflicts with existing packages

### Authentication Issues

```bash
# Configure PyPI token
# Create ~/.pypirc with your tokens:
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token
```

### Version Updates

To upload a new version:

1. Update version in `pyproject.toml`
2. Update version in `gpt_image_2_polza_mcp_server/__init__.py`
3. Rebuild and upload

```bash
# Update version and rebuild
uv run python scripts/build.py
uv run python scripts/upload.py
```

## Package Structure Summary

Your package is now structured for PyPI:

```
nanobanana-mcp-server/
├── gpt_image_2_polza_mcp_server/          # Main package
│   ├── __init__.py                 # Package metadata
│   ├── server.py                   # Entry point
│   ├── config/                     # Configuration
│   ├── core/                       # Core functionality
│   ├── services/                   # Business logic
│   ├── tools/                      # MCP tools
│   ├── resources/                  # MCP resources
│   ├── prompts/                    # Prompt templates
│   └── utils/                      # Utilities
├── scripts/
│   ├── build.py                    # Build automation
│   └── upload.py                   # Upload automation
├── pyproject.toml                  # Package configuration
└── README.md                       # Documentation
```

## After Successful Upload

1. **Update Documentation**: Add PyPI installation instructions to README
2. **Create GitHub Release**: Tag the version and create a release
3. **Announce**: Share on relevant communities and social media
4. **Monitor**: Watch for issues and user feedback

Your MCP server is now ready for distribution via PyPI and uvx! 🎉