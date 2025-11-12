#!/usr/bin/env bash
# scripts/docs-serve.sh
# Serve documentation locally with live reload

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Starting Documentation Server${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""
echo -e "${GREEN}Starting MkDocs server...${NC}"
echo -e "${GREEN}Check output below for URL${NC}"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop${NC}"
echo ""

uv run mkdocs serve
