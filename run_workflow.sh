#!/bin/bash

# Wrapper script for design work statistics workflow
# Handles Python version selection and runs the full pipeline

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use Python 3.11 (most stable)
PYTHON_BIN="/opt/homebrew/opt/python@3.11/bin/python3.11"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Python 3.11 not found at $PYTHON_BIN"
    exit 1
fi

echo "📊 Starting design work statistics workflow..."
echo "🕐 $(date)"

# Run statistics and save data
echo ""
echo "1️⃣ Gathering statistics from Google Sheets..."
$PYTHON_BIN stats_improved.py

# Run chart generation and upload
echo ""
echo "2️⃣ Generating charts..."
$PYTHON_BIN generate_charts.py

echo ""
echo "✅ Workflow completed successfully!"
echo "🕐 $(date)"
