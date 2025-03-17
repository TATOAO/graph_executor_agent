"""
MCP Client Example - A simple demonstration of how to use the MCP server.
"""

import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# Configure logging

async def main():
    """Run the MCP client example."""
    # Create an MCP client with SSE transport
    print('Connecting to MCP server...')
    async with sse_client("http://localhost:8000/sse") as (read_stream, write_stream):
        # why the process hangs here?
        # because the server is not sending the initialization response
        # so the client is waiting for the initialization response
        # and the process hangs
        client = ClientSession(read_stream=read_stream, write_stream=write_stream)
        
        print("Connecting to MCP server...")
        
        # Initialize the session
        await client.initialize()

        # Get server info
        server_info = await client.get_server_info()
        print(f"Server Info: {json.dumps(server_info, indent=2)}")
        
        # List available prompts
        prompts = await client.list_prompts()
        print(f"\nAvailable Prompts: {json.dumps(prompts, indent=2)}")
        
        # Get a prompt
        greeting_prompt = await client.get_prompt("greeting")
        print(f"\nGreeting Prompt: {greeting_prompt}")
        
        # Get a parameterized prompt
        weather_prompt = await client.get_prompt("weather_inquiry", parameters={"city": "London"})
        print(f"\nWeather Inquiry Prompt: {weather_prompt}")
        
        # List available resources
        resources = await client.list_resources()
        print(f"\nAvailable Resources: {json.dumps(resources, indent=2)}")
        
        # Get a resource
        weather = await client.get_resource("weather://london")
        print(f"\nLondon Weather: {weather}")
        
        # Get a random fact
        fact = await client.get_resource("facts://random")
        print(f"\nRandom Fact: {fact}")
        
        # List available tools
        tools = await client.list_tools()
        print(f"\nAvailable Tools: {json.dumps(tools, indent=2)}")
        
        # Use a tool
        bmi_result = await client.use_tool("calculate_bmi", parameters={"weight_kg": 70, "height_m": 1.75})
        print(f"\nBMI Calculation: {json.dumps(bmi_result, indent=2)}")
        
        # Use another tool
        temp_result = await client.use_tool(
            "convert_temperature", 
            parameters={"value": 32, "from_unit": "F", "to_unit": "C"}
        )
        print(f"\nTemperature Conversion: {json.dumps(temp_result, indent=2)}")
        
        # Use the word count tool
        word_count_result = await client.use_tool(
            "word_count", 
            parameters={"text": "This is a sample text for word counting. It has multiple words and characters."}
        )
        print(f"\nWord Count: {json.dumps(word_count_result, indent=2)}")
        
        # Use the echo tool
        echo_result = await client.use_tool(
            "echo_with_context", 
            parameters={"message": "Hello from MCP client!"}
        )
        print(f"\nEcho Result: {echo_result}")

if __name__ == "__main__":
    asyncio.run(main()) 
