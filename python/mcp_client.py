import asyncio
import sys
from mcp.client.stdio import stdio_client, StdioClientParams
from mcp.client.session import ClientSession
from mcp.common.types import TextContent # ToolParameterValue might not be directly needed if dict works

# It's good practice to ensure the server is in the same directory or adjust path
# For this example, we assume mcp_server.py is in the current working directory
# when this client is run, or on Python's path.
# The CWD for StdioClientParams will be set to "." (meaning the directory from which this client is run).


async def call_echo_tool(session: ClientSession, message: str) -> str:
    """Calls the 'echo' tool on the server and returns the text response."""
    try:
        # For the echo tool, the argument is named "message".
        tool_result = await session.call_tool(name="echo", arguments={"message": message})

        # Process the result - FastMCP tools that return a single string
        # usually wrap it in a list of TextContent.
        if tool_result.content and isinstance(tool_result.content, list) and len(tool_result.content) > 0:
            first_content = tool_result.content[0]
            if isinstance(first_content, TextContent) and hasattr(first_content, 'text'):
                return first_content.text
            elif isinstance(first_content, dict) and 'text' in first_content: # Handle if it's a dict, not TextContent obj
                return first_content['text']
            elif isinstance(first_content, str):  # If it's just a plain string in the list
                return first_content
        
        # Fallback or error if the structure is not as expected
        error_message = f"Error: Could not parse echo tool result or result was empty. Result: {tool_result}"
        print(error_message, file=sys.stderr)
        return error_message
    except Exception as e:
        error_detail = f"Exception during 'echo' tool call: {e}"
        print(error_detail, file=sys.stderr)
        return error_detail


async def main():
    # Assuming mcp_client.py is in the 'python' directory, and mcp_server.py is also there.
    # If python/mcp_server.py is intended, and client is run from repo root, path should be "python/mcp_server.py"
    # For simplicity, assuming client is run from within the 'python' directory itself.
    server_command = [sys.executable, "mcp_server.py"]
    
    # StdioClientParams takes the command and cwd.
    # If this script (mcp_client.py) is in python/, and mcp_server.py is also in python/,
    # then cwd="." is correct if running mcp_client.py from the python/ directory.
    server_params = StdioClientParams(command=server_command, cwd=".")
    
    try:
        print("Attempting to start and connect to MCP server...")
        # The stdio_client context manager handles starting and stopping the server process.
        async with stdio_client(server_params) as (reader, writer):
            print("Connected to server's stdio. Initializing client session...")
            async with ClientSession(reader=reader, writer=writer, client_name="python-mcp-client") as session:
                print("Client session started. Initializing MCP session...")
                # Send empty capabilities, server will respond with its own
                init_response = await session.initialize(server_capabilities={}) 
                if init_response and init_response.server_info:
                    print(f"Server initialized: Name={init_response.server_info.name}, Version={init_response.server_info.version}")
                else:
                    print("Server initialization response not as expected or failed.", file=sys.stderr)
                    return # Cannot proceed without successful initialization

                # Call the echo tool
                echo_message = "Hello MCP!"
                print(f"\nCalling 'echo' tool with message: '{echo_message}'")
                echo_response = await call_echo_tool(session, echo_message)
                print(f"--> 'echo' tool response: '{echo_response}'")

                # Call the 'add' tool
                a_val, b_val = 5, 7
                print(f"\nCalling 'add' tool with a={a_val}, b={b_val}")
                add_response_structured = await session.call_tool(name="add", arguments={"a": a_val, "b": b_val})
                
                add_response_text = f"Error: Could not parse 'add' tool result. Result: {add_response_structured}"
                if add_response_structured.content and \
                   isinstance(add_response_structured.content, list) and \
                   len(add_response_structured.content) > 0:
                    first_content_add = add_response_structured.content[0]
                    if isinstance(first_content_add, TextContent) and hasattr(first_content_add, 'text'):
                        add_response_text = first_content_add.text
                    elif isinstance(first_content_add, dict) and 'text' in first_content_add:
                         add_response_text = first_content_add['text']

                print(f"--> 'add' tool response: '{add_response_text}'")
                print("\nClient operations complete.")

    except ConnectionRefusedError:
        print("Connection to MCP server failed. Ensure the server script (mcp_server.py) is executable and correctly configured.", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Server script 'mcp_server.py' not found in the current directory. Ensure paths are correct. CWD for server: {server_params.cwd}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        # If stdio_client started a process, it should handle its termination on exit.
        # If not, manual process management might be needed here for robustness in case of early errors.
    finally:
        print("Client finished.")


if __name__ == "__main__":
    asyncio.run(main())
