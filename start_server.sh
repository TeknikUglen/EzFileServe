#!/bin/bash
# Resolve the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtualenv relative to script location
source "$SCRIPT_DIR/../venv/bin/activate"

# Move to the app directory
cd "$SCRIPT_DIR"

# Start gunicorn
exec gunicorn -w 4 -b 0.0.0.0:8000 app:app
