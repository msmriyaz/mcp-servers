import asyncio
import json
from dotenv import load_dotenv
from pathlib import Path

# MCP Server Imports
from mcp import types as mcp_types  # Use alias to avoid conflict with genai.types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Import the weather tools
from agent import get_weather, get_forecast, get_alerts, get_current_time

# Load environment variables from the same directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

print("Starting Weather MCP Server initialization...")

# --- MCP Server Setup ---
print("Creating MCP Server instance...")
# Create a named MCP Server instance
app = Server("weather-mcp-server")

# Implement the MCP server's @app.list_tools handler
@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """MCP handler to list available tools."""
    print("MCP Server: Received list_tools request.")
    
    # Define the tools we want to expose
    tools = [
        mcp_types.Tool(
            name="get_weather",
            description="Get current weather for a location anywhere in the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for"
                    }
                },
                "required": ["location"]
            }
        ),
        mcp_types.Tool(
            name="get_forecast",
            description="Get weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get forecast for"
                    }
                },
                "required": ["location"]
            }
        ),
        mcp_types.Tool(
            name="get_alerts",
            description="Get weather alerts for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get alerts for"
                    }
                },
                "required": ["location"]
            }
        ),
        mcp_types.Tool(
            name="get_current_time",
            description="Get current time for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get time for"
                    }
                },
                "required": ["location"]
            }
        )
    ]
    
    print(f"MCP Server: Advertising {len(tools)} tools")
    return tools

# Implement the MCP server's @app.call_tool handler
@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[mcp_types.TextContent | mcp_types.ImageContent | mcp_types.EmbeddedResource]:
    """MCP handler to execute a tool call."""
    print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")

    try:
        # Map the tool name to the appropriate function
        tool_functions = {
            "get_weather": get_weather,
            "get_forecast": get_forecast,
            "get_alerts": get_alerts,
            "get_current_time": get_current_time
        }
        
        if name in tool_functions:
            # Execute the appropriate function
            result = tool_functions[name](**arguments)
            
            if result["status"] == "success":
                return [mcp_types.TextContent(type="text", text=result["report"])]
            else:
                return [mcp_types.TextContent(type="text", text=result["error_message"])]
        else:
            error_text = json.dumps({"error": f"Tool '{name}' not implemented."})
            return [mcp_types.TextContent(type="text", text=error_text)]
            
    except Exception as e:
        print(f"MCP Server: Error executing tool '{name}': {e}")
        error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
        return [mcp_types.TextContent(type="text", text=error_text)]

# --- MCP Server Runner ---
async def run_server():
    """Runs the MCP server over standard input/output."""
    # Use the stdio_server context manager from the MCP library
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("MCP Server starting handshake...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        print("MCP Server run loop finished.")

if __name__ == "__main__":
    print("Launching Weather MCP Server...")
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user.")
    except Exception as e:
        print(f"MCP Server encountered an error: {e}")
    finally:
        print("MCP Server process exiting.") 