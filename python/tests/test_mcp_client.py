import pytest
import asyncio
import sys
import os
from mcp import StdioServerParameters # Changed import
from mcp.client.stdio import stdio_client # Changed import
from mcp.client.session import ClientSession

# Assuming mcp_client.py and mcp_server.py are in the parent directory of 'tests'
# when pytest is run from the 'python' directory.
try:
    from mcp_client import call_echo_tool
except ImportError:
    import pathlib
    PYTHON_DIR_PATH = str(pathlib.Path(__file__).parent.parent.resolve())
    if PYTHON_DIR_PATH not in sys.path:
        sys.path.insert(0, PYTHON_DIR_PATH)
    from mcp_client import call_echo_tool

@pytest.mark.anyio
async def test_successful_echo():
    """
    Tests the call_echo_tool function by starting the mcp_server.py,
    sending a message, and asserting the echoed response.
    """
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.dirname(current_file_dir)
    server_cwd = python_dir
    python_executable = sys.executable

    # Changed to StdioServerParameters and adjusted arguments
    server_params = StdioServerParameters(
        command=python_executable,
        args=["mcp_server.py"], 
        cwd=server_cwd
    )
    
    test_message = "Pytest says hello to the echo tool!"
    expected_response = f"Echo: {test_message}"
    actual_response = None

    try:
        print("[TEST_LOG] Attempting to enter stdio_client context...", flush=True)
        async with stdio_client(server_params) as (reader, writer):
            print("[TEST_LOG] Entered stdio_client context. Attempting to enter ClientSession context...", flush=True)
            async with ClientSession(reader, writer) as session:
                print("[TEST_LOG] Entered ClientSession context. Attempting to initialize session...", flush=True)
                await session.initialize()
                print("[TEST_LOG] Session initialized. Attempting to call_echo_tool...", flush=True)
                actual_response = await call_echo_tool(session, test_message)
                print(f"[TEST_LOG] call_echo_tool returned: {actual_response}", flush=True)
            print("[TEST_LOG] Exited ClientSession context.", flush=True)
        print("[TEST_LOG] Exited stdio_client context.", flush=True)
                
    except FileNotFoundError:
        pytest.fail(f"Server script 'mcp_server.py' not found in CWD: {server_cwd}. sys.executable: {python_executable}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during test setup or execution: {e}")

    assert actual_response == expected_response, \
        f"Echo tool did not return the expected response. Expected: '{expected_response}', Got: '{actual_response}'"
