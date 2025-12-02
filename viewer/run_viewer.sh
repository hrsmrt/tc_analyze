#!/bin/bash
# TC Analysis Viewer launcher script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIEWER_SCRIPT="$SCRIPT_DIR/tc_viewer.py"

echo "================================================"
echo "  TC Analysis Viewer"
echo "================================================"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: Streamlit is not installed"
    echo ""
    echo "Please install required packages:"
    echo "  pip install streamlit pillow"
    echo ""
    exit 1
fi

# Check if viewer script exists
if [ ! -f "$VIEWER_SCRIPT" ]; then
    echo "Error: Viewer script not found: $VIEWER_SCRIPT"
    exit 1
fi

echo "Starting Streamlit viewer..."
echo "Current directory: $(pwd)"
echo "Viewer will search for 'fig' directory or 'script/setting.json'"
echo ""

# Launch Streamlit app from current directory
streamlit run "$VIEWER_SCRIPT"

echo ""
echo "Viewer closed."
