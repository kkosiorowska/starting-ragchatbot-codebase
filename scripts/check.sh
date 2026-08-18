#!/bin/bash
# Verify the codebase is formatted correctly without making changes.
# Exits non-zero (and lists the affected files) if formatting is needed.

set -e

echo "Checking black formatting..."
uv run black --check --diff backend main.py

echo "All files are properly formatted."
