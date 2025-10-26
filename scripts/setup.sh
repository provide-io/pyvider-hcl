#!/usr/bin/env bash
# scripts/setup.sh
# Full development environment setup for pyvider-hcl

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}pyvider-hcl Development Setup${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv is not installed${NC}"
    echo -e "${YELLOW}Install uv: https://docs.astral.sh/uv/getting-started/installation/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ uv found${NC}"

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${python_version}${NC}"

# Sync dependencies
echo -e "${BLUE}Syncing dependencies...${NC}"
uv sync
echo -e "${GREEN}✓ Dependencies synced${NC}"

# Verify installation
echo -e "${BLUE}Verifying installation...${NC}"
uv run python -c "import pyvider.hcl; print(f'pyvider-hcl {pyvider.hcl.__version__}')"
echo -e "${GREEN}✓ Package importable${NC}"

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  Run tests:        ${YELLOW}make test${NC}"
echo -e "  Format code:      ${YELLOW}make format${NC}"
echo -e "  Run linter:       ${YELLOW}make lint${NC}"
echo -e "  Type check:       ${YELLOW}make typecheck${NC}"
echo -e "  Quality checks:   ${YELLOW}make quality${NC}"
echo -e "  Build docs:       ${YELLOW}make docs${NC}"
echo -e "  See all targets:  ${YELLOW}make help${NC}"
echo ""
