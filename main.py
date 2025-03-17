"""
MCP Server Demo - A simple demonstration of a Model Context Protocol server.
"""

import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from mcp.types import PromptMessage, TextContent
from starlette.responses import StreamingResponse
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MCP Server Demo")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create SSE transport
sse_transport = SseServerTransport("/messages/")

# Create MCP server
mcp = FastMCP(app=app)

# Define some example data
WEATHER_DATA = {
    "new york": "Sunny, 75°F",
    "london": "Rainy, 60°F",
    "tokyo": "Cloudy, 70°F",
    "sydney": "Clear, 80°F",
    "paris": "Partly cloudy, 65°F",
}

FACTS = [
    "The Great Wall of China is not visible from space with the naked eye.",
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.",
    "A day on Venus is longer than a year on Venus. Venus takes 243 Earth days to rotate once on its axis but only 225 Earth days to orbit the Sun.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "The average cloud weighs about 1.1 million pounds.",
]

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "mcp-server-demo"}

# SSE endpoint
@app.get("/sse")
async def handle_sse(request: Request):
    async def event_generator() -> AsyncGenerator[bytes, None]:
        try:
            logger.info("Starting SSE connection")
            # Create a custom send function that properly handles ASGI messages
            async def custom_send(message):
                print(message)
                message_type = message.get("type")
                print("Message type:", message_type)
                if message_type == "http.response.start":
                    # Store the headers but don't send the start message
                    headers = [
                        [b"content-type", b"text/event-stream"],
                        [b"cache-control", b"no-cache"],
                        [b"connection", b"keep-alive"],
                        [b"x-accel-buffering", b"no"]
                    ]
                    message["headers"] = headers
                    # Don't send the start message, just store it
                    return
                elif message_type == "http.response.body":
                    # Send the body message
                    await request._send(message)
                else:
                    # Handle other message types
                    await request._send(message)

            logger.info("Establishing SSE connection")
            async with sse_transport.connect_sse(
                request.scope, request.receive, custom_send
            ) as streams:
                logger.info("SSE connection established, starting MCP server")
                try:
                    # Send initialization response
                    init_response = {
                        "jsonrpc": "2.0",
                        "id": 0,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "sampling": {},
                                "roots": {
                                    "listChanged": True
                                }
                            },
                            "serverInfo": {
                                "name": "mcp-server-demo",
                                "version": "0.1.0"
                            }
                        }
                    }
                    logger.info("Sending initialization response")
                    yield f"data: {json.dumps(init_response)}\n\n".encode()
                    
                    # Start the MCP server
                    logger.info("Starting MCP server")
                    await mcp._mcp_server.run(
                        streams[0],
                        streams[1],
                        mcp._mcp_server.create_initialization_options()
                    )
                except Exception as e:
                    logger.error(f"Error in MCP server run: {str(e)}", exc_info=True)
                    error_message = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "error": {
                            "code": -32000,
                            "message": str(e),
                            "data": None
                        }
                    }
                    yield f"data: {json.dumps(error_message)}\n\n".encode()
                    return
        except Exception as e:
            logger.error(f"Error in SSE connection: {str(e)}", exc_info=True)
            error_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32000,
                    "message": str(e),
                    "data": None
                }
            }
            yield f"event: message\ndata: {json.dumps(error_message)}\n\n".encode()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Message endpoint
@app.post("/messages/")
async def handle_post_message(request: Request):
    try:
        # Read the body once and store it
        body = await request.body()
        if not body:
            logger.warning("Received empty message body")
            return {"status": "error", "message": "Empty message body"}
            
        logger.info(f"Received message: {body}")
        
        # Create a custom send function for the message endpoint
        async def custom_send(message):
            if message["type"] == "http.response.start":
                return
            await request._send(message)
            
        # Create a new request with the stored body
        async def receive():
            return {"type": "http.request.body", "body": body, "more_body": False}
            
        await sse_transport.handle_post_message(
            request.scope, receive, custom_send
        )
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

# Define prompts
@mcp.prompt()
def greeting() -> str:
    """A simple greeting prompt."""
    return "Hello! I'm an AI assistant. How can I help you today?"

@mcp.prompt()
def weather_inquiry(city: str) -> str:
    """A prompt for inquiring about weather in a specific city."""
    return f"What's the weather like in {city} today?"

@mcp.prompt()
def code_review(code: str, language: str) -> str:
    """A prompt for requesting a code review."""
    return f"""Please review this {language} code and provide feedback:

```{language}
{code}
```

Please consider:
1. Code correctness
2. Best practices
3. Potential bugs
4. Performance issues
5. Readability"""

@mcp.prompt()
def conversation_starter(topic: str) -> List[PromptMessage]:
    """A prompt that starts a conversation about a specific topic."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=f"Let's talk about {topic}.")
        ),
        PromptMessage(
            role="assistant",
            content=TextContent(type="text", text="That's an interesting topic! What aspects of it would you like to explore?")
        )
    ]

# Define resources
@mcp.resource("weather://{city}")
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    city_lower = city.lower()
    if city_lower in WEATHER_DATA:
        return WEATHER_DATA[city_lower]
    return f"Weather data for {city} is not available."

@mcp.resource("facts://random")
def get_random_fact() -> str:
    """Get a random interesting fact."""
    import random
    return random.choice(FACTS)

@mcp.resource("facts://all")
def get_all_facts() -> List[str]:
    """Get all available interesting facts."""
    return FACTS

# Define tools
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> Dict[str, Any]:
    """
    Calculate BMI (Body Mass Index) given weight in kg and height in meters.
    
    Args:
        weight_kg: Weight in kilograms
        height_m: Height in meters
        
    Returns:
        Dictionary with BMI value and category
    """
    if weight_kg <= 0 or height_m <= 0:
        return {"error": "Weight and height must be positive values"}
    
    bmi = weight_kg / (height_m ** 2)
    
    # Determine BMI category
    category = ""
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category
    }

@mcp.tool()
def convert_temperature(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin.
    
    Args:
        value: The temperature value to convert
        from_unit: The unit to convert from ('C', 'F', or 'K')
        to_unit: The unit to convert to ('C', 'F', or 'K')
        
    Returns:
        Dictionary with the converted value
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()
    
    # Validate units
    valid_units = ['C', 'F', 'K']
    if from_unit not in valid_units or to_unit not in valid_units:
        return {"error": "Units must be 'C', 'F', or 'K'"}
    
    # Convert to Celsius first
    if from_unit == 'C':
        celsius = value
    elif from_unit == 'F':
        celsius = (value - 32) * 5/9
    else:  # Kelvin
        celsius = value - 273.15
    
    # Convert from Celsius to target unit
    if to_unit == 'C':
        result = celsius
    elif to_unit == 'F':
        result = celsius * 9/5 + 32
    else:  # Kelvin
        result = celsius + 273.15
    
    return {
        "original_value": value,
        "original_unit": from_unit,
        "converted_value": round(result, 2),
        "converted_unit": to_unit
    }

@mcp.tool()
def word_count(text: str) -> Dict[str, Any]:
    """
    Count the number of words, characters, and lines in a text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with word, character, and line counts
    """
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines()) or 1  # At least 1 line
    
    return {
        "word_count": words,
        "character_count": chars,
        "line_count": lines,
        "average_word_length": round(chars / words, 2) if words > 0 else 0
    }

@mcp.tool()
async def echo_with_context(message: str, ctx: Context) -> str:
    """
    Echo a message back with some context information.
    
    Args:
        message: The message to echo
        ctx: The MCP context object
        
    Returns:
        The echoed message with context information
    """
    # Log the request
    logger.info(f"Echo request received: {message}")
    
    # Get request ID from context
    request_id = ctx.request_context.request_id
    
    return f"Echo: {message}\nRequest ID: {request_id}\nTimestamp: {ctx.request_context.timestamp}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
