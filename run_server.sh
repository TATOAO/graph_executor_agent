#!/bin/bash

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the server
echo "Starting MCP server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 