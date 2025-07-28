#!/bin/bash

# Set Chrome binary and driver path
export CHROME_BIN="/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"
export PATH="/opt/render/project/.render:$PATH"

# Launch app
gunicorn app:app --bind 0.0.0.0:$PORT
