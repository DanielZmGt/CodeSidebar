#!/bin/bash
echo "Starting CodeSidebar..."
# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
"$DIR/venv/bin/python3" "$DIR/main.py"
