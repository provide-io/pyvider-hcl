#!/usr/bin/env bash
# scripts/test.sh
# Enhanced test runner with coverage and reporting

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default options
PARALLEL=${PARALLEL:-true}
COVERAGE=${COVERAGE:-true}
VERBOSE=${VERBOSE:-false}
MARKER=${MARKER:-""}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-parallel)
            PARALLEL=false
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -m|--marker)
            MARKER="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-parallel    Disable parallel test execution"
            echo "  --no-coverage    Disable coverage reporting"
            echo "  -v, --verbose    Enable verbose output"
            echo "  -m, --marker     Run tests with specific marker (unit, integration, slow)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Running pyvider-hcl Tests${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Build pytest command
PYTEST_CMD="uv run pytest"

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
    echo -e "${BLUE}Mode: Parallel${NC}"
else
    echo -e "${BLUE}Mode: Sequential${NC}"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=pyvider.hcl --cov-report=html --cov-report=term-missing"
    echo -e "${BLUE}Coverage: Enabled${NC}"
fi

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vvv"
    echo -e "${BLUE}Verbosity: High${NC}"
fi

if [ -n "$MARKER" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKER"
    echo -e "${BLUE}Marker: $MARKER${NC}"
fi

echo ""
echo -e "${BLUE}Running: $PYTEST_CMD${NC}"
echo ""

# Run tests
if $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}✓ All tests passed${NC}"
    echo -e "${GREEN}==================================${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}Coverage report: htmlcov/index.html${NC}"
    fi

    exit 0
else
    echo ""
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}✗ Tests failed${NC}"
    echo -e "${RED}==================================${NC}"
    exit 1
fi
