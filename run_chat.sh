#!/bin/bash

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Please run run_server.sh first to set up the environment."
    exit 1
fi

source venv/bin/activate

# Run the chat client
echo "Starting MCP chat client..."
python chat_client.py 