import pytest
import asyncio
import sys
import os # For path manipulation if needed, though not strictly for this version

# Assuming mcp_client.py and mcp_server.py are in the parent directory of 'tests'
# when pytest is run from the 'python' directory.
# If pytest is run from the project root, sys.path might need adjustment or use python.module
try:
    from mcp_client import call_echo_tool
except ImportError:
    # This block allows running pytest from the project root (e.g., "pytest python/tests")
    # by temporarily adding the 'python' directory to the path.
    # It's a common workaround but might not be ideal for all setups.
    # A better long-term solution would be proper packaging or using PYTHONPATH.
    import pathlib
    PYTHON_DIR_PATH = str(pathlib.Path(__file__).parent.parent.resolve())
    if PYTHON_DIR_PATH not in sys.path:
        sys.path.insert(0, PYTHON_DIR_PATH)
    from mcp_client import call_echo_tool


from mcp.client.stdio import StdioClientParams, stdio_client
from mcp.client.session import ClientSession

@pytest.mark.asyncio
async def test_successful_echo():
    """
    Tests the call_echo_tool function by starting the mcp_server.py,
    sending a message, and asserting the echoed response.
    """
    # Determine path to mcp_server.py relative to this test file.
    # This test file is in python/tests/test_mcp_client.py
    # mcp_server.py is in python/
    # So, mcp_server.py is in the parent directory of this test file's directory.
    
    # Assuming pytest is run from the project root, or that the python directory is discoverable.
    # The command should point to "python/mcp_server.py".
    # The CWD for the server process should be "python/" so it can find constants.py.
    
    # Path setup:
    # If pytest is run from project root:
    #   server_script_path = "python/mcp_server.py"
    #   server_cwd = "python"
    # If pytest is run from python/ directory:
    #   server_script_path = "mcp_server.py"
    #   server_cwd = "."

    # Let's try to make it robust to where pytest is run from (root or python/ dir)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.dirname(current_file_dir) # This should be the 'python' directory

    server_script_path = os.path.join(python_dir, "mcp_server.py")
    server_cwd = python_dir # Server's CWD should be the 'python' directory

    # Check if we are in a CI environment or similar where sys.executable is preferred
    # For local dev, if a venv is active, sys.executable is fine.
    python_executable = sys.executable 

    server_params = StdioClientParams(
        command=[python_executable, server_script_path], 
        cwd=server_cwd
    )
    
    test_message = "Pytest says hello to the echo tool!"
    expected_response = f"Echo: {test_message}"
    actual_response = None

    try:
        async with stdio_client(server_params) as (reader, writer):
            async with ClientSession(reader=reader, writer=writer, client_name="pytest-mcp-client") as session:
                await session.initialize(server_capabilities={})
                
                # Call the echo tool function from the client module
                actual_response = await call_echo_tool(session, test_message)
                
    except FileNotFoundError:
        pytest.fail(f"Server script not found. Looked for: {server_script_path} with CWD: {server_cwd}. sys.executable: {python_executable}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during test setup or execution: {e}")

    assert actual_response == expected_response, \
        f"Echo tool did not return the expected response. Expected: '{expected_response}', Got: '{actual_response}'"

# Example of how to run this test (assuming pytest is installed):
# From the project root:
# pytest python/tests/test_mcp_client.py
# Or from the python/ directory:
# pytest tests/test_mcp_client.py
