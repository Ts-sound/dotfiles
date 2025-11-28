#!/bin/bash

set -e

# current script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# terminal directory
TERMINAL_DIR="$(pwd)"

# export to PATH


echo $SCRIPT_DIR
echo $TERMINAL_DIR

python3 "$SCRIPT_DIR/install_extensions.py" "$@"
