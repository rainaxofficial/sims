#!/bin/bash

# Point Selenium to installed Chrome binary
export CHROME_BIN="/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"
export PATH="$CHROME_BIN:$PATH"

gunicorn app:app --bind 0.0.0.0:$PORT
