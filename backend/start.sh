#!/bin/bash
# Activate venv if present (local dev); on Railway the global env is used
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
