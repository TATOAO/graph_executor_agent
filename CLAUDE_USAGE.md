# Using the MCP Server with Claude

This guide explains how to use the Model Context Protocol (MCP) server with Claude Desktop or other Claude interfaces.

## Overview

The Model Context Protocol (MCP) allows Claude to access external tools, data sources, and prompts through a standardized interface. This server provides several capabilities:

1. **Prompts**: Pre-defined templates for common tasks
2. **Resources**: Endpoints for retrieving data (like weather information or facts)
3. **Tools**: Functions that perform calculations or actions (like BMI calculation or temperature conversion)

## Setting Up Claude Desktop with MCP

1. Install Claude Desktop from the official website
2. Open Claude Desktop and go to Settings
3. Navigate to the "Model Context Protocol" section
4. Add a new MCP server with the URL `http://localhost:8000` (or your server's address)
5. Save the settings

## Available Capabilities

### Prompts

- `greeting`: A simple greeting prompt
- `weather_inquiry`: A prompt for asking about weather in a specific city
- `code_review`: A prompt for requesting a code review
- `conversation_starter`: A prompt that starts a conversation about a specific topic

### Resources

- `weather://{city}`: Get weather information for a city
- `facts://random`: Get a random interesting fact
- `facts://all`: Get all available interesting facts

### Tools

- `calculate_bmi`: Calculate BMI given weight and height
- `convert_temperature`: Convert temperature between Celsius, Fahrenheit, and Kelvin
- `word_count`: Count words, characters, and lines in a text
- `echo_with_context`: Echo a message back with context information

## Example Prompts for Claude

Here are some example prompts you can use with Claude when the MCP server is connected:

1. "What's the weather like in London today?"
2. "Tell me an interesting fact."
3. "Can you calculate my BMI? I'm 70kg and 1.75m tall."
4. "Convert 32°F to Celsius."
5. "How many words are in this message?"

## Troubleshooting

If Claude is unable to connect to the MCP server:

1. Ensure the server is running (`./run_server.sh`)
2. Check that the server URL is correctly configured in Claude Desktop
3. Verify that your firewall allows connections to the server port (8000 by default)
4. Check the server logs for any error messages

## Advanced Usage

For more advanced usage, you can:

1. Modify the server code to add your own prompts, resources, and tools
2. Use the client examples (`client_example.py` and `chat_client.py`) to test the server
3. Integrate the MCP server with other applications that support the Model Context Protocol 