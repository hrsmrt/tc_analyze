#!/bin/bash
# TC Analysis Viewer launcher script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "  TC Analysis Viewer"
echo "================================================"
echo ""
echo "Starting Streamlit viewer..."
echo "Project root: $PROJECT_ROOT"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: Streamlit is not installed"
    echo ""
    echo "Please install required packages:"
    echo "  pip install streamlit pillow"
    echo ""
    exit 1
fi

# Launch Streamlit app
streamlit run viewer/tc_viewer.py

echo ""
echo "Viewer closed."
