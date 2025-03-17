#!/bin/bash

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Please run run_server.sh first to set up the environment."
    exit 1
fi

source venv/bin/activate

# Run the client
echo "Starting MCP client..."
python client_example.py 