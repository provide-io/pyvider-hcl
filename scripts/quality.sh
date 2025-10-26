#!/usr/bin/env bash
# scripts/quality.sh
# Run all code quality checks

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

FAILED=0

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Code Quality Checks${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Format check
echo -e "${BLUE}[1/3] Checking code formatting...${NC}"
if uv run ruff format . --check; then
    echo -e "${GREEN}✓ Format check passed${NC}"
else
    echo -e "${RED}✗ Format check failed${NC}"
    echo -e "${YELLOW}Run 'make format' to fix${NC}"
    FAILED=1
fi
echo ""

# Lint check
echo -e "${BLUE}[2/3] Running linter...${NC}"
if uv run ruff check .; then
    echo -e "${GREEN}✓ Linter passed${NC}"
else
    echo -e "${RED}✗ Linter failed${NC}"
    echo -e "${YELLOW}Run 'make lint-fix' to auto-fix some issues${NC}"
    FAILED=1
fi
echo ""

# Type check
echo -e "${BLUE}[3/3] Running type checker...${NC}"
if uv run mypy src/; then
    echo -e "${GREEN}✓ Type check passed${NC}"
else
    echo -e "${RED}✗ Type check failed${NC}"
    FAILED=1
fi
echo ""

# Summary
echo -e "${BLUE}==================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All quality checks passed${NC}"
    echo -e "${GREEN}==================================${NC}"
    exit 0
else
    echo -e "${RED}✗ Some quality checks failed${NC}"
    echo -e "${RED}==================================${NC}"
    exit 1
fi
