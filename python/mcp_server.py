import asyncio
import os
import json
import base64
import random # Added random
from contextlib import asynccontextmanager
from enum import Enum
from mcp.server.fast_mcp import FastMCP, Context
from mcp.messages import UserMessage, TextContent, ImageContent, AssistantMessage
from .constants import MCP_TINY_IMAGE
# import mcp # For mcp.run() # Removed as per instructions

# Define PromptName Enum at module level
class PromptName(Enum):
    SIMPLE = "simple_prompt"
    COMPLEX = "complex_prompt"

# ALL_RESOURCES constant
ALL_RESOURCES = [
    {
        "uri": "test://static/resource/1",
        "name": "Resource 1",
        "mime_type": "text/plain",
        "text": "Resource 1: This is a plaintext resource"
    },
    {
        "uri": "test://static/resource/2",
        "name": "Resource 2",
        "mime_type": "application/octet-stream",
        "blob": base64.b64encode(b"Resource 2: This is a base64 blob").decode('utf-8')
    },
    {
        "uri": "test://static/resource/3",
        "name": "Resource 3 - Another Text",
        "mime_type": "text/plain",
        "text": "Resource 3: More plaintext content here."
    },
    {
        "uri": "test://static/resource/4",
        "name": "Resource 4 - Image (Fake)",
        "mime_type": "image/png",
        "blob": base64.b64encode(b"Fake PNG data").decode('utf-8')
    },
    {
        "uri": "test://static/resource/5",
        "name": "Resource 5 - JSON Data",
        "mime_type": "application/json",
        "text": json.dumps({"key": "value", "number": 123})
    },
    {
        "uri": "test://static/resource/6",
        "name": "Resource 6 - Long Text",
        "mime_type": "text/plain",
        "text": "This is resource number six, and it has a slightly longer description to see how text wrapping or truncation might be handled by a client."
    },
    {
        "uri": "test://static/resource/7",
        "name": "Resource 7 - Another Blob",
        "mime_type": "application/octet-stream",
        "blob": base64.b64encode(b"Yet another piece of binary data for Resource 7").decode('utf-8')
    }
]

# EXAMPLE_COMPLETIONS constant
EXAMPLE_COMPLETIONS = {
    "style": ["casual", "formal", "technical", "friendly"],
    "temperature": ["0", "0.5", "0.7", "1.0"],
    "resourceId": ["1", "2", "3", "4", "5"], 
}

# Logging constants and helper
LOG_LEVEL_ORDER = ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"]
LOG_MESSAGES = [
    {"level": "debug", "data": "This is a debug message: Variable x = 10"},
    {"level": "info", "data": "Service started successfully on port 8080."},
    {"level": "notice", "data": "User 'admin' logged in from IP 192.168.1.100."},
    {"level": "warning", "data": "Disk space is nearing capacity (90% used)."},
    {"level": "error", "data": "Failed to connect to database: Connection timed out."},
    {"level": "critical", "data": "Critical system failure: Unable to allocate memory."},
    {"level": "alert", "data": "Security alert: Possible intrusion detected."},
    {"level": "emergency", "data": "System is shutting down due to an emergency."}
]

def is_message_ignored(current_level_str: str, message_level_str: str) -> bool:
    try:
        current_idx = LOG_LEVEL_ORDER.index(current_level_str.lower())
        message_idx = LOG_LEVEL_ORDER.index(message_level_str.lower())
        return message_idx < current_idx
    except ValueError: 
        return True 

async def main():
    # Initialization for subscriptions and periodic task
    subscriptions: set[str] = set()
    subs_update_interval_task: asyncio.Task | None = None
    
    # Initialization for logging
    log_level: str = "debug" # Default log level
    logs_update_interval_task: asyncio.Task | None = None


    # Periodic resource update notification function
    async def notify_resource_updates(server_ref: FastMCP):
        while True:
            await asyncio.sleep(5)
            for uri in list(subscriptions):
                try:
                    await server_ref.notify_resource_updated(uri)
                except Exception as e:
                    pass 

    # Periodic log message notification function
    async def notify_log_messages(server_ref: FastMCP):
        nonlocal log_level # To access the current log_level from main's scope
        while True:
            await asyncio.sleep(15) # 15-second interval
            random_message = random.choice(LOG_MESSAGES)
            if not is_message_ignored(log_level, random_message["level"]):
                try:
                    await server_ref.notify_message(
                        level=random_message["level"],
                        data=random_message["data"],
                        logger="python-mcp-server" 
                    )
                except Exception as e:
                    # Potentially log this error to stderr or a file if server_ref.notify_message fails
                    print(f"Error sending log message: {e}")


    # Lifespan context manager
    @asynccontextmanager
    async def app_lifespan(app: FastMCP):
        nonlocal subs_update_interval_task, logs_update_interval_task
        print("[SERVER_LOG][LIFESPAN] Startup: Entered app_lifespan.", flush=True)
        
        # Startup
        subs_update_interval_task = asyncio.create_task(notify_resource_updates(app))
        logs_update_interval_task = asyncio.create_task(notify_log_messages(app))
        print("[SERVER_LOG][LIFESPAN] Startup: Background tasks created.", flush=True)
        
        try:
            yield
            print("[SERVER_LOG][LIFESPAN] Normal execution, pre-shutdown.", flush=True)
        finally:
            print("[SERVER_LOG][LIFESPAN] Shutdown: Entered finally block.", flush=True)
            # Shutdown
            tasks_to_cancel = []
            if subs_update_interval_task:
                subs_update_interval_task.cancel()
                tasks_to_cancel.append(subs_update_interval_task)
            if logs_update_interval_task:
                logs_update_interval_task.cancel()
                tasks_to_cancel.append(logs_update_interval_task)
            
            if tasks_to_cancel:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
                print("[SERVER_LOG][LIFESPAN] Shutdown: Background tasks gathered.", flush=True)
            print("[SERVER_LOG][LIFESPAN] Shutdown: app_lifespan cleanup complete.", flush=True)


    server = FastMCP(
        name="python-mcp-everything",
        version="0.1.0",
        capabilities={
            "prompts": {}, 
            "resources": {"subscribe": True}, 
            "logging": {}  # Indicates logging capability
        },
        lifespan=app_lifespan 
    )

    # --- Logging Control Handler ---
    @server.set_logging_level_handler()
    async def set_logging_level_handler(level: str, ctx: Context) -> None:
        nonlocal log_level
        log_level = level.lower() # Normalize to lower case
        # Notify client about the change. Using "info" level for this notification itself.
        await ctx.notify_message(
            level="info", 
            data=f"Logging level set to: {log_level}", 
            logger="python-mcp-server"
        )

    # Echo tool
    @server.tool()
    def echo(message: str) -> str:
        return f"Echo: {message}"

    # Add tool
    @server.tool()
    def add(a: int, b: int) -> str:
        return f"The sum of {a} and {b} is {a + b}."

    # LongRunningOperation tool
    @server.tool()
    async def long_running_operation(duration: int = 10, steps: int = 5, ctx: Context = None) -> str:
        for i in range(steps):
            await asyncio.sleep(duration / steps)
            if ctx: 
                await ctx.report_progress(current_step=i + 1, total_steps=steps)
        return f"Long running operation completed. Duration: {duration} seconds, Steps: {steps}."

    # PrintEnv tool
    @server.tool()
    def print_env() -> str:
        return json.dumps(dict(os.environ), indent=2)

    # SampleLLM tool
    @server.tool()
    async def sample_llm(prompt: str, max_tokens: int = 100, ctx: Context = None) -> str:
        if not ctx:
            return "Error: Context not available for LLM sampling."
        response_message = await ctx.create_message(
            messages=[UserMessage(content=TextContent(text=prompt))],
            max_tokens=max_tokens
        )
        if response_message and hasattr(response_message, 'content') and hasattr(response_message.content, 'text'):
            result_text = response_message.content.text
            return f"LLM sampling result: {result_text}"
        else:
            return "LLM sampling result: (Could not extract text from response)"

    # GetTinyImage tool
    @server.tool()
    def get_tiny_image() -> list:
        return [
            TextContent(text="This is a tiny image:"),
            ImageContent(data=MCP_TINY_IMAGE, mime_type="image/png"),
            TextContent(text="The image above is the MCP tiny image.")
        ]

    # AnnotatedMessage tool
    @server.tool()
    def annotated_message(message_type: str, include_image: bool = False) -> list:
        content_parts = []
        if message_type == "error":
            content_parts.append(TextContent(
                text="Error: Operation failed",
                annotations={"priority": 1.0, "audience": ["user", "assistant"]}
            ))
        elif message_type == "success":
            content_parts.append(TextContent(
                text="Operation completed successfully",
                annotations={"priority": 0.7, "audience": ["user"]}
            ))
        elif message_type == "debug":
            content_parts.append(TextContent(
                text="Debug: Cache hit ratio 0.95, latency 150ms",
                annotations={"priority": 0.3, "audience": ["assistant"]}
            ))
        else:
            content_parts.append(TextContent(
                text=f"Unknown message type: {message_type}",
                annotations={"priority": 0.5, "audience": ["user", "assistant"]}
            ))
        if include_image:
            content_parts.append(ImageContent(
                data=MCP_TINY_IMAGE,
                mime_type="image/png",
                annotations={"priority": 0.5, "audience": ["user"]}
            ))
        return content_parts

    # --- Resource Listing Logic ---
    PAGE_SIZE_RESOURCES = 10 
    async def list_all_static_resources(cursor: str | None = None, page_size: int = PAGE_SIZE_RESOURCES, ctx: Context = None) -> tuple[list[dict], str | None]:
        start_index = 0
        if cursor:
            try:
                decoded_cursor = int(base64.b64decode(cursor).decode('utf-8'))
                start_index = decoded_cursor 
            except Exception as e:
                if ctx and hasattr(ctx, 'error'): 
                    await ctx.error(f"Invalid cursor format received: {cursor}. Error: {e}")
                start_index = 0
        actual_page_size = page_size if page_size > 0 else PAGE_SIZE_RESOURCES
        end_index = min(start_index + actual_page_size, len(ALL_RESOURCES))
        resources_page = ALL_RESOURCES[start_index:end_index]
        next_cursor_val = None
        if end_index < len(ALL_RESOURCES):
            next_cursor_val = base64.b64encode(str(end_index).encode('utf-8')).decode('utf-8')
        return resources_page, next_cursor_val
    server.set_list_resources_handler(list_all_static_resources, prefix="test://static/resource/")

    @server.resource("test://static/resource/{resource_id}")
    async def get_static_resource(resource_id: str, ctx: Context = None) -> dict:
        uri_to_find = f"test://static/resource/{resource_id}"
        resource = next((r for r in ALL_RESOURCES if r["uri"] == uri_to_find), None)
        if resource:
            return resource
        else:
            raise ValueError(f"Resource with ID {resource_id} not found.")

    @server.list_resource_templates_handler()
    async def list_resource_templates_handler(ctx: Context = None) -> list:
        return [
            {
                "uri_template": "test://static/resource/{resource_id}",
                "name": "Static Resource",
                "description": "A static resource with a numeric ID.",
                "parameters": [{"name": "resource_id", "description": "The unique identifier for the static resource."}]
            }
        ]

    # --- Prompt Handling Logic ---
    @server.list_prompts_handler()
    async def list_prompts_handler(ctx: Context = None) -> list:
        return [
            {
                "name": PromptName.SIMPLE.value,
                "description": "A prompt without arguments",
                "arguments": [] 
            },
            {
                "name": PromptName.COMPLEX.value,
                "description": "A prompt with arguments",
                "arguments": [
                    {"name": "temperature", "description": "Temperature setting", "required": True},
                    {"name": "style", "description": "Output style", "required": False},
                ],
            },
        ]

    @server.get_prompt_handler()
    async def get_prompt_handler(name: str, arguments: dict[str, any] | None = None, ctx: Context = None) -> dict:
        if name == PromptName.SIMPLE.value:
            return {"messages": [UserMessage(content=TextContent(text="This is a simple prompt without arguments."))]}
        elif name == PromptName.COMPLEX.value:
            temp = arguments.get("temperature") if arguments else None
            style = arguments.get("style") if arguments else None
            return {
                "messages": [
                    UserMessage(content=TextContent(text=f"This is a complex prompt with arguments: temperature={temp}, style={style}")),
                    AssistantMessage(content=TextContent(text="I understand. You've provided a complex prompt with temperature and style arguments. How would you like me to proceed?")),
                    UserMessage(content=ImageContent(data=MCP_TINY_IMAGE, mime_type="image/png"))
                ]
            }
        else:
            raise ValueError(f"Unknown prompt: {name}")

    # --- Argument Completion Logic ---
    @server.completion_handler()
    async def completion_handler(ref: dict, argument: dict, ctx: Context = None) -> dict:
        arg_name = argument.get("name")
        arg_value_str = str(argument.get("value", "")).lower()
        
        completions_to_return = []

        if arg_name in EXAMPLE_COMPLETIONS:
            source_list = EXAMPLE_COMPLETIONS[arg_name]
            completions_to_return = [item for item in source_list if item.lower().startswith(arg_value_str)]
        
        return {
            "completion": {
                "values": completions_to_return,
                "has_more": False, 
                "total": len(completions_to_return),
            }
        }

    # Subscribe handler
    @server.subscribe_handler()
    async def subscribe_handler(uri: str, ctx: Context) -> None:
        subscriptions.add(uri)
        await ctx.info(f"Client subscribed to resource: {uri}")

    # Unsubscribe handler
    @server.unsubscribe_handler()
    async def unsubscribe_handler(uri: str, ctx: Context) -> None:
        subscriptions.discard(uri)
        await ctx.info(f"Client unsubscribed from resource: {uri}")

    print("[SERVER_LOG] Server setup complete. Attempting to start server.run()...", flush=True)
    try:
        await server.run()
        print("[SERVER_LOG] server.run() completed.", flush=True) # Might not be reached if it blocks
    except Exception as e:
        print(f"[SERVER_LOG] Exception from server.run(): {e}", flush=True)
    finally:
        print("[SERVER_LOG] main() function is exiting.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
