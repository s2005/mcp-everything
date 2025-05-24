#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]"]
"""
Minecraft Proxy Server
"""

from mcp.server.fastmcp import FastMCP

def echo(message: str) -> str:
    """Echoes the input message."""
    return message

if __name__ == '__main__':
    server = FastMCP(server_name="EchoServer")
    server.run(transport="stdio")
