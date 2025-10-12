#!/usr/bin/env bash
# Test installation script for orchestrator-toolkit
# This script creates a clean test environment and validates the package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Orchestrator Toolkit Installation Test${NC}"
echo "================================================"

# Create temporary test directory
TEST_DIR="/tmp/otk_test_$(date +%s)"
echo -e "${YELLOW}Creating test directory: $TEST_DIR${NC}"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create and activate virtual environment
echo -e "${YELLOW}Setting up virtual environment...${NC}"
python3 -m venv test_env
source test_env/bin/activate

# Install from PyPI Test
echo -e "${YELLOW}Installing orchestrator-toolkit from PyPI Test...${NC}"
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            orchestrator-toolkit

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
pip show orchestrator-toolkit

# Set environment variable
export OTK_ARTIFACT_ROOT=.ai_docs

# Test commands
echo -e "${GREEN}Testing commands...${NC}"

echo "1. Creating a task..."
task-new "Test task from installation script" --owner TestUser
if [ -f ".ai_docs/tasks/T-0001.md" ]; then
    echo -e "${GREEN}✓ Task created successfully${NC}"
    cat .ai_docs/tasks/T-0001.md
else
    echo -e "${RED}✗ Task creation failed${NC}"
    exit 1
fi

echo ""
echo "2. Creating a plan..."
plan-new "Test plan" --owner TestUser
if [ -f ".ai_docs/plans/P-0001.md" ]; then
    echo -e "${GREEN}✓ Plan created successfully${NC}"
else
    echo -e "${RED}✗ Plan creation failed${NC}"
    exit 1
fi

echo ""
echo "3. Running orchestrator..."
orchestrator-once
echo -e "${GREEN}✓ Orchestrator ran successfully${NC}"

echo ""
echo "4. Testing alternate command names..."
otk-task-new "Another test task" --owner TestUser2
if [ -f ".ai_docs/tasks/T-0002.md" ]; then
    echo -e "${GREEN}✓ otk-task-new works${NC}"
else
    echo -e "${RED}✗ otk-task-new failed${NC}"
    exit 1
fi

# Test Python import
echo ""
echo "5. Testing Python import..."
python -c "
from orchestrator_toolkit.settings import OrchSettings
settings = OrchSettings.load()
print(f'✓ Python import successful')
print(f'  Tasks directory: {settings.tasks_dir}')
print(f'  Plans directory: {settings.plans_dir}')
"

# Summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All tests passed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo "Test artifacts created in: $TEST_DIR/.ai_docs/"
echo ""
echo "To clean up test directory, run:"
echo "  rm -rf $TEST_DIR"
echo ""
echo "To deactivate virtual environment, run:"
echo "  deactivate"