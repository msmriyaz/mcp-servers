import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
import sys

# Load environment variables from .env file in the parent directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# --- Step 1: Import Tools from MCP Server ---
async def get_tools_async():
    """Gets tools from the Weather MCP Server."""
    print("Attempting to connect to Weather MCP server...")
    tools, exit_stack = await MCPToolset.from_server(
        # Use StdioServerParameters for local process communication
        connection_params=StdioServerParameters(
            command=sys.executable,  # Command to run the server
            args=[str(Path(__file__).parent / "weather_mcp_server.py")],
        )
    )
    print("MCP Toolset created successfully.")
    # MCP requires maintaining a connection to the local MCP Server.
    # exit_stack manages the cleanup of this connection.
    return tools, exit_stack

# --- Step 2: Agent Definition ---
async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server."""
    tools, exit_stack = await get_tools_async()
    print(f"Fetched {len(tools)} tools from MCP server.")
    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='weather_assistant',
        instruction='Help users get weather information, forecasts, alerts, and time for any city worldwide.',
        tools=list(tools),  # Convert to list instead of tuple
    )
    return root_agent, exit_stack

async def main():
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={}, app_name='weather_mcp_app', user_id='user_weather'
    )

    query = "What's the weather like in Sydney, Australia?"
    print(f"\nUser Query: '{query}'")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    try:
        root_agent, exit_stack = await get_agent_async()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return

    runner = Runner(
        app_name='weather_mcp_app',
        agent=root_agent,
        session_service=session_service,
    )

    print("\nRunning agent...")
    try:
        events_async = runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content
        )

        async for event in events_async:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f"\nAgent: {part.text}")
                    elif hasattr(part, 'function_call') and part.function_call:
                        print(f"\nCalling: {part.function_call.name}")
                        if hasattr(part.function_call, 'args'):
                            print(f"Arguments: {part.function_call.args}")
                    elif hasattr(part, 'function_response') and part.function_response:
                        if hasattr(part.function_response, 'response'):
                            print(f"\nResult: {part.function_response.response}")

    except Exception as e:
        print(f"\nError during agent execution: {e}")
    finally:
        print("\nClosing MCP server connection...")
        await exit_stack.aclose()
        print("Cleanup complete.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWeather MCP Client stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc() 