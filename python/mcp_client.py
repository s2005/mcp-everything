import asyncio
import sys
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters # Changed import
from mcp.client.session import ClientSession
from mcp.types import TextContent


async def call_echo_tool(session: ClientSession, message: str) -> str:
    """Calls the 'echo' tool on the server and returns the text response."""
    try:
        tool_result = await session.call_tool(name="echo", arguments={"message": message})
        if tool_result.content and isinstance(tool_result.content, list) and len(tool_result.content) > 0:
            first_content = tool_result.content[0]
            if isinstance(first_content, TextContent) and hasattr(first_content, 'text'):
                return first_content.text
            elif isinstance(first_content, dict) and 'text' in first_content:
                return first_content['text']
            elif isinstance(first_content, str):
                return first_content
        error_message = f"Error: Could not parse echo tool result or result was empty. Result: {tool_result}"
        print(error_message, file=sys.stderr)
        return error_message
    except Exception as e:
        error_detail = f"Exception during 'echo' tool call: {e}"
        print(error_detail, file=sys.stderr)
        return error_detail


async def main():
    server_executable = sys.executable # Changed variable name
    server_args = ["mcp_server.py"]      # Changed variable name
    
    # Use StdioServerParameters and pass command and args separately
    server_params = StdioServerParameters(command=server_executable, args=server_args, cwd=".") # Changed class and params
    
    try:
        print("Attempting to start and connect to MCP server...")
        async with stdio_client(server_params) as (reader, writer):
            print("Connected to server's stdio. Initializing client session...")
            async with ClientSession(reader, writer) as session:
                print("Client session started. Initializing MCP session...")
                init_response = await session.initialize(server_capabilities={})
                if init_response and init_response.server_info:
                    print(f"Server initialized: Name={init_response.server_info.name}, Version={init_response.server_info.version}")
                else:
                    print("Server initialization response not as expected or failed.", file=sys.stderr)
                    return

                echo_message = "Hello MCP!"
                print(f"\nCalling 'echo' tool with message: '{echo_message}'")
                echo_response = await call_echo_tool(session, echo_message)
                print(f"--> 'echo' tool response: '{echo_response}'")

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
        # Corrected to refer to server_args[0] for the script name
        print(f"Error: Server script '{server_args[0]}' not found in the current directory. Ensure paths are correct. CWD for server: {server_params.cwd}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        print("Client finished.")


if __name__ == "__main__":
    asyncio.run(main())
