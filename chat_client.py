"""
MCP Chat Client - A simple chat interface that uses the MCP server.
"""

import asyncio
import json
import sys
import os
from typing import List, Dict, Any, Optional
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types

class MCPChatClient:
    """A simple chat client that uses the MCP server."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """Initialize the chat client."""
        self.server_url = server_url
        self.session = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.available_tools: List[str] = []
        self.available_resources: List[str] = []
        self.available_prompts: List[str] = []
    
    async def initialize(self):
        """Initialize the client by fetching available tools, resources, and prompts."""
        try:
            # Create SSE client and get streams
            async with sse_client(self.server_url) as (read_stream, write_stream):
                # Create client session
                self.session = ClientSession(read_stream, write_stream)
                await self.session.initialize()
                
                # Get server info
                server_info = await self.session.send_request(
                    types.ClientRequest(
                        types.GetServerInfoRequest(method="server/info")
                    ),
                    types.GetServerInfoResult
                )
                print(f"Connected to MCP server: {server_info.get('name', 'Unknown')}")
                
                # Get available tools
                tools = await self.session.list_tools()
                self.available_tools = [tool["id"] for tool in tools]
                print(f"Available tools: {', '.join(self.available_tools)}")
                
                # Get available resources
                resources = await self.session.list_resources()
                self.available_resources = [resource["id"] for resource in resources]
                print(f"Available resources: {', '.join(self.available_resources)}")
                
                # Get available prompts
                prompts = await self.session.list_prompts()
                self.available_prompts = [prompt["id"] for prompt in prompts]
                print(f"Available prompts: {', '.join(self.available_prompts)}")
                
                # Start with a greeting prompt
                greeting = await self.session.get_prompt("greeting")
                print("\n" + "=" * 50)
                print("Assistant: " + greeting)
                print("=" * 50 + "\n")
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": greeting
                })
                
        except Exception as e:
            print(f"Error initializing client: {e}")
            sys.exit(1)
    
    async def process_command(self, command: str) -> Optional[str]:
        """Process a special command."""
        if command == "/help":
            return """
Available commands:
/help - Show this help message
/tools - List available tools
/resources - List available resources
/prompts - List available prompts
/clear - Clear the conversation history
/exit - Exit the chat

To use a tool: /tool <tool_name> <param1>=<value1> <param2>=<value2> ...
To get a resource: /resource <resource_uri>
To use a prompt: /prompt <prompt_id> <param1>=<value1> <param2>=<value2> ...
"""
        elif command == "/tools":
            return f"Available tools: {', '.join(self.available_tools)}"
        
        elif command == "/resources":
            return f"Available resources: {', '.join(self.available_resources)}"
        
        elif command == "/prompts":
            return f"Available prompts: {', '.join(self.available_prompts)}"
        
        elif command == "/clear":
            self.conversation_history = []
            return "Conversation history cleared."
        
        elif command.startswith("/tool "):
            # Parse tool command: /tool tool_name param1=value1 param2=value2
            parts = command[6:].strip().split()
            if not parts:
                return "Error: Tool name is required."
            
            tool_name = parts[0]
            if tool_name not in self.available_tools:
                return f"Error: Tool '{tool_name}' not found."
            
            # Parse parameters
            params = {}
            for param in parts[1:]:
                if "=" not in param:
                    return f"Error: Invalid parameter format '{param}'. Use param=value."
                
                key, value = param.split("=", 1)
                # Try to convert to appropriate type
                try:
                    # Try as number
                    if "." in value:
                        params[key] = float(value)
                    else:
                        params[key] = int(value)
                except ValueError:
                    # Keep as string
                    params[key] = value
            
            try:
                result = await self.session.call_tool(tool_name, arguments=params)
                return f"Tool result: {json.dumps(result, indent=2)}"
            except Exception as e:
                return f"Error using tool: {e}"
        
        elif command.startswith("/resource "):
            # Parse resource command: /resource resource_uri
            resource_uri = command[10:].strip()
            try:
                result = await self.session.read_resource(resource_uri)
                return f"Resource content: {json.dumps(result, indent=2)}"
            except Exception as e:
                return f"Error getting resource: {e}"
        
        elif command.startswith("/prompt "):
            # Parse prompt command: /prompt prompt_id param1=value1 param2=value2
            parts = command[8:].strip().split()
            if not parts:
                return "Error: Prompt ID is required."
            
            prompt_id = parts[0]
            if prompt_id not in self.available_prompts:
                return f"Error: Prompt '{prompt_id}' not found."
            
            # Parse parameters
            params = {}
            for param in parts[1:]:
                if "=" not in param:
                    return f"Error: Invalid parameter format '{param}'. Use param=value."
                
                key, value = param.split("=", 1)
                params[key] = value
            
            try:
                result = await self.session.get_prompt(prompt_id, arguments=params)
                return f"Prompt: {result}"
            except Exception as e:
                return f"Error getting prompt: {e}"
        
        return None
    
    async def run(self):
        """Run the chat client."""
        await self.initialize()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ")
                
                # Check for exit command
                if user_input.strip() == "/exit":
                    print("Goodbye!")
                    break
                
                # Check for special commands
                if user_input.startswith("/"):
                    result = await self.process_command(user_input)
                    if result:
                        print("\n" + "=" * 50)
                        print(result)
                        print("=" * 50 + "\n")
                    continue
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Process user input using MCP tools and resources
                # This is a simplified example - in a real application, you would use an LLM
                # to determine which tools and resources to use based on the user input
                
                # For this demo, we'll just echo the user input and provide some basic responses
                response = f"You said: {user_input}"
                
                # Check for some keywords to demonstrate tool usage
                if "weather" in user_input.lower():
                    # Extract city name (simplified)
                    city = "london"  # Default
                    for known_city in ["new york", "london", "tokyo", "sydney", "paris"]:
                        if known_city in user_input.lower():
                            city = known_city
                            break
                    
                    try:
                        weather = await self.session.read_resource(f"weather://{city}")
                        response = f"The weather in {city.title()} is: {weather}"
                    except Exception as e:
                        response = f"Sorry, I couldn't get the weather information: {e}"
                
                elif "fact" in user_input.lower():
                    try:
                        fact = await self.session.read_resource("facts://random")
                        response = f"Here's an interesting fact: {fact}"
                    except Exception as e:
                        response = f"Sorry, I couldn't get a fact: {e}"
                
                elif "bmi" in user_input.lower():
                    response = "To calculate BMI, use the command: /tool calculate_bmi weight_kg=<weight> height_m=<height>"
                
                elif "temperature" in user_input.lower() and "convert" in user_input.lower():
                    response = "To convert temperature, use the command: /tool convert_temperature value=<value> from_unit=<C/F/K> to_unit=<C/F/K>"
                
                elif "count" in user_input.lower() and ("word" in user_input.lower() or "character" in user_input.lower()):
                    response = "To count words and characters, use the command: /tool word_count text=<your text>"
                
                # Add response to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Display response
                print("\n" + "=" * 50)
                print("Assistant: " + response)
                print("=" * 50 + "\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

async def main():
    """Run the MCP chat client."""
    # Get server URL from environment variable or use default
    server_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
    
    # Create and run the chat client
    chat_client = MCPChatClient(server_url=server_url)
    await chat_client.run()

if __name__ == "__main__":
    asyncio.run(main()) 