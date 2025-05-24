# MCP Echo Server

This script implements a simple Model Context Protocol (MCP) server using Python and the `fastMCP` library from the `modelcontextprotocol` Python SDK.

## Description

The server provides a single tool named `echo_tool`. This tool accepts a string of text as input and returns the identical string as output. The server communicates using the `stdio` (standard input/output) transport mechanism.

This server is intended as a basic example of an MCP server.

## Requirements

- Python 3.12 or higher

## Dependencies

The script uses `uv` for managing dependencies, as specified in the header:
- `mcp[cli]`

To install dependencies using `uv`:
```bash
uv pip install "mcp[cli]"
```
Or, if you have `uv` manage the script directly, it should handle dependencies automatically.

## Running the Script

You can run the server directly using a Python interpreter:

```bash
python mcp_server.py
```

Alternatively, if you are using `uv` and it's configured to run scripts:

```bash
uv run mcp_server.py
```

Once running, the server will listen for MCP messages on its standard input and send responses to its standard output.

## How it Works

1.  The script starts with a `uv` script header specifying the Python version and dependencies.
2.  It imports `FastMCP` from `mcp.server.fastmcp`.
3.  An instance of `FastMCP` is created, named "EchoServer".
4.  An `echo_tool` function is defined and decorated with `@mcp.tool()`. This tool takes a `text` string and returns it.
5.  The main execution block (`if __name__ == '__main__':`) calls `mcp.run(transport="stdio")` to start the server.
```
