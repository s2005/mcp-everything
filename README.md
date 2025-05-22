# MCP Everything

**Note:** This project was extracted from https://github.com/modelcontextprotocol/servers/tree/main/src/everything to create a standalone implementation.

This MCP server project demonstrates various features of the Model Context Protocol (MCP). It includes server implementations in TypeScript and Python, serving as test servers for MCP client builders. Both implementations aim for functional parity, showcasing capabilities like prompts, tools, resources, sampling, logging, and more.

## Common Features

### Tools

1. `echo`
   - Simple tool to echo back input messages
   - Input:
     - `message` (string): Message to echo back
   - Returns: Text content with echoed message

2. `add`
   - Adds two numbers together
   - Inputs:
     - `a` (number): First number
     - `b` (number): Second number
   - Returns: Text result of the addition

3. `longRunningOperation`
   - Demonstrates progress notifications for long operations
   - Inputs:
     - `duration` (number, default: 10): Duration in seconds
     - `steps` (number, default: 5): Number of progress steps
   - Returns: Completion message with duration and steps
   - Sends progress notifications during execution

4. `sampleLLM`
   - Demonstrates LLM sampling capability using MCP sampling feature
   - Inputs:
     - `prompt` (string): The prompt to send to the LLM
     - `maxTokens` (number, default: 100): Maximum tokens to generate
   - Returns: Generated LLM response

5. `getTinyImage`
   - Returns a small test image
   - No inputs required
   - Returns: Base64 encoded PNG image data

6. `printEnv`
   - Prints all environment variables
   - Useful for debugging MCP server configuration
   - No inputs required
   - Returns: JSON string of all environment variables

7. `annotatedMessage`
   - Demonstrates how annotations can be used to provide metadata about content
   - Inputs:
     - `messageType` (enum: "error" | "success" | "debug"): Type of message to demonstrate different annotation patterns
     - `includeImage` (boolean, default: false): Whether to include an example image
   - Returns: Content with varying annotations

### Resources

The server provides 100 test resources in two formats:
- Even numbered resources:
  - Plaintext format
  - URI pattern: `test://static/resource/{even_number}`
  - Content: Simple text description

- Odd numbered resources:
  - Binary blob format
  - URI pattern: `test://static/resource/{odd_number}`
  - Content: Base64 encoded binary data

Resource features:
- Supports pagination (10 items per page)
- Allows subscribing to resource updates
- Demonstrates resource templates
- Auto-updates subscribed resources every 5 seconds

### Prompts

1. `simple_prompt`
   - Basic prompt without arguments
   - Returns: Single message exchange

2. `complex_prompt`
   - Advanced prompt demonstrating argument handling
   - Required arguments:
     - `temperature` (number): Temperature setting
   - Optional arguments:
     - `style` (string): Output style preference
   - Returns: Multi-turn conversation with images

### Logging

The server sends random-leveled log messages every 15 seconds to demonstrate the logging capabilities of MCP.

## TypeScript Implementation

**Location:** `typescript/`

### Installation

#### Local Development

```bash
# Clone the repository (if not already done)
# git clone https://github.com/modelcontextprotocol/mcp-everything.git
# cd mcp-everything

# Navigate to the TypeScript directory from the repository root
cd typescript

# Install dependencies
npm install

# Build the project
npm run build

# Start the server
npm start
```

#### Global Installation

```bash
# Navigate to the TypeScript directory:
# cd path/to/mcp-everything/typescript
# Then install globally from the local package:
npm install -g .

# Run the server 
# (The command name will depend on the 'bin' field in typescript/package.json, 
#  e.g., 'mcp-everything-ts' or 'mcp-everything' if modified)
# Example:
# mcp-everything-ts
```
*Note: Global installation functionality and the exact command depend on the `bin` configuration within `typescript/package.json`.*

#### Docker

```bash
# Build the Docker image from the repository root
# (Assumes Dockerfile is updated to handle APP_DIR build argument or typescript context)
docker build -t mcp-everything-ts -f Dockerfile . --build-arg APP_DIR=typescript

# Run the container
docker run -it mcp-everything-ts
```

### Usage with MCP Clients (e.g., Claude Desktop)

Add to your client's MCP server configuration. Paths might need adjustment.

If using `npx` with a published package (e.g., `mcp-everything-ts`):
```json
{
  "mcpServers": {
    "everything-ts-npx": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-everything-ts" 
        // Replace 'mcp-everything-ts' with the actual package name if different
      ]
    }
  }
}
```
If running from a local build (ensure `cwd` is the `typescript` directory):
```json
{
  "mcpServers": {
    "everything-ts-local": {
      "command": "npm",
      "args": [
        "start"
      ],
      // Ensure 'cwd' points to the 'typescript' directory of this project.
      "cwd": "path/to/mcp-everything/typescript" 
    }
  }
}
```
Replace `"path/to/mcp-everything/typescript"` with the correct path.

---

## Python Implementation

**Location:** `python/`

### Installation & Setup

1.  From the repository root, navigate to the Python directory:
    ```bash
    cd python
    ```
2.  (Recommended) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install "mcp[cli]"
    ```

### Running the Server

From within the `python` directory (and with the virtual environment activated if used):
```bash
python mcp_server.py
```
The server listens for MCP messages over stdio.

### Usage with MCP Clients (e.g., Claude Desktop)

Example configuration:
```json
{
  "mcpServers": {
    "everything-py": {
      "command": "python", // Or "path/to/python/venv/bin/python"
      "args": ["mcp_server.py"],
      "cwd": "path/to/mcp-everything/python" // Ensure this is the correct path
    }
  }
}
```
Replace `"path/to/mcp-everything/python"` with the correct path.