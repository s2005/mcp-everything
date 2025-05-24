#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]"]
# ///
"""
MCP Echo Server

This script implements a simple server using the FastMCP framework
from the modelcontextprotocol Python SDK. It defines an "echo_tool"
that simply returns any text it receives. The server is configured
to communicate over standard input/output (stdio).
"""

# Import the FastMCP class from the mcp.server.fastmcp module.
# FastMCP is the core class for creating MCP servers.
from mcp.server.fastmcp import FastMCP

# Instantiate the FastMCP server.
# The `server_name` parameter gives a name to this server instance.
# This instance is created at the module level so that the @mcp.tool decorator
# can register tools with it when the module is loaded.
mcp = FastMCP(server_name="EchoServer")

# Define the echo tool.
# The @mcp.tool() decorator registers this function as a tool
# that can be called by an MCP client.
@mcp.tool()
def echo_tool(text: str) -> str:
    """Echo the input text"""
    # This tool simply returns the 'text' argument it receives.
    return text

# This is the main execution block that runs when the script is executed directly.
if __name__ == '__main__':
    # Start the server and run its main loop.
    # The `transport="stdio"` argument configures the server to use
    # standard input and standard output for communication. This means
    # it will read requests from stdin and send responses to stdout.
    mcp.run(transport="stdio")
