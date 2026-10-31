import sys
from pathlib import Path

path = Path(__file__).resolve().parents[1]
if str(path) not in sys.path:
    sys.path.insert(0, str(path))
    
from functions.run_python_file_in_shell import execute_python_code_from_shell, execute_python_code_from_shell_function
from functions.run_python_file import run_python_file, run_python_file_function
from functions.write_file import write_file, write_file_function
from functions.get_files_info import get_file_info, get_file_info_function
from functions.get_file_content import get_file_content,get_file_content_function
from functions.write_new_file import write_new_file, write_new_file_function
from functions.wikitool import get_wikipedia_info, get_wikipedia_info_function
from functions.summariser import get_summerized_content, get_summerized_content_function
from shell_tools.directory_tools import run_shell_command, run_shell_command_function
from functions.save_memory import save_memory, save_memory_function
from functions.save_todo_updates import save_todo, save_todo_function
from functions.save_execution_ledger import save_exe_ledger, save_exe_ledger_function
import asyncio
import inspect
import logging

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


logger = logging.getLogger(__name__)
handler = logging.FileHandler('batching_tool.log')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# --------------------------------------------------
# 1. TOOL SPECIFICATION
# --------------------------------------------------

@dataclass
class ToolSpec:
    name: str
    handler: Callable
    description: str
    definition: Optional[dict] = None
    required_args: tuple = ()
    allowed_args: Optional[tuple] = None


# --------------------------------------------------
# 2. TOOL REGISTRY
# --------------------------------------------------

class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec):
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")

        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        return self._tools[name]

    def get_definitions(self) -> list[dict]:
        return [
            spec.definition
            for spec in self._tools.values()
            if spec.definition is not None
        ]

    def names(self) -> list[str]:
        return list(self._tools.keys())


# --------------------------------------------------
# 3. REGISTER TOOLS
# --------------------------------------------------

registry = ToolRegistry()

tool_configs = [
    ("run_python_file", run_python_file, run_python_file_function),
    ("write_file", write_file, write_file_function),
    ("get_file_info", get_file_info, get_file_info_function),
    ("get_file_content", get_file_content, get_file_content_function),
    ("write_new_file", write_new_file, write_new_file_function),
    ("get_wikipedia_info", get_wikipedia_info, get_wikipedia_info_function),
    ("get_summerized_content", get_summerized_content, get_summerized_content_function),
    ("run_shell_command", run_shell_command, run_shell_command_function),
    ("execute_python_code_from_shell", execute_python_code_from_shell, execute_python_code_from_shell_function),
    ("save_memory", save_memory, save_memory_function),
    ("save_todo", save_todo, save_todo_function),
    ("save_exe_ledger", save_exe_ledger, save_exe_ledger_function)
]

for name, handler, definition in tool_configs:
    registry.register(
        ToolSpec(
            name=name,
            handler=handler,
            description=f"Execute {name}",
            definition=definition
        )
    )


# --------------------------------------------------
# 4. TOOL ARGUMENT VALIDATION
# --------------------------------------------------

def validate_arguments(spec: ToolSpec, args: Any):

    if not isinstance(args, dict):
        raise TypeError("tool_args must be a dictionary")

    missing = set(spec.required_args) - args.keys()

    if missing:
        raise ValueError(
            f"Missing required arguments: {sorted(missing)}"
        )

    if spec.allowed_args is not None:
        unexpected = args.keys() - set(spec.allowed_args)

        if unexpected:
            raise ValueError(
                f"Unexpected arguments: {sorted(unexpected)}"
            )

    return args


# --------------------------------------------------
# 5. SINGLE TOOL EXECUTION
# --------------------------------------------------

async def execute_one_tool(tool_call: dict):

    tool_name = tool_call.get("tool_name")

    try:
        spec = registry.get(tool_name)

        args = validate_arguments(
            spec,
            tool_call.get("tool_args")
        )

        handler = spec.handler

        # Support both synchronous and asynchronous functions.
        if inspect.iscoroutinefunction(handler):
            result = await handler(**args)
        else:
            result = await asyncio.to_thread(handler, **args)

            # Handle synchronous wrappers returning awaitables.
            if inspect.isawaitable(result):
                result = await result

        return {
            "tool_name": tool_name,
            "status": "success",
            "result": result,
            "error": None
        }

    except Exception as exc:
        logger.exception("Tool execution failed: %s", tool_name)

        return {
            "tool_name": tool_name,
            "status": "error",
            "result": None,
            "error": str(exc)
        }


# --------------------------------------------------
# 6. BATCH EXECUTION
# --------------------------------------------------

async def batched_tools(
    tools: list[dict],
    max_concurrency: int = 5,
    parallel: bool = True
):

    if not isinstance(tools, list):
        return {
            "status": "error",
            "error": "Invalid argument: tools must be a list."
        }

    if not isinstance(max_concurrency, int) or isinstance(max_concurrency, bool) or max_concurrency < 1:
        return {
            "status": "error",
            "error": "Invalid argument: max_concurrency must be a positive integer."
        }

    semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_with_limit(tool):
        async with semaphore:
            return await execute_one_tool(tool)

    if parallel:
        results = await asyncio.gather(
            *(execute_with_limit(tool) for tool in tools)
        )
    else:
        results = []

        for tool in tools:
            results.append(
                await execute_with_limit(tool)
            )

    return results


# async def main():

#     tools = [
#         {
#             "call_id": "call_001",
#             "tool_name": "get_file_info",
#             "tool_args": {
#                 # Your existing tool arguments
#             }
#         },
#         {
#             "call_id": "call_002",
#             "tool_name": "get_file_content",
#             "tool_args": {
#                 # Your existing tool arguments
#             }
#         }
#     ]

#     results = await batched_tools(
#         tools,
#         max_concurrency=5,
#         parallel=True
#     )

#     for result in results:
#         print(result)


# asyncio.run(main())


batched_tools_function = {
    "type": "function",
    "name": "batched_tools",
    "description": """
            Executes multiple registered tools through a single invocation.
            Use this tool when multiple operations are required to accomplish
            a task. Independent operations should be executed in parallel.
            Set parallel=false when operations have execution dependencies
            and must run sequentially.

            Each nested tool must be registered and its arguments must
            satisfy that tool's schema.
        """,

    "parameters": {
        "type": "object",
        "properties": {
            "tools": {
                "type": "array",
                "description": """The working directory. An example of argument:
                            tools = [
                                {
                                    "tool_name": "get_file_info",
                                    "tool_args": {
                                        # Your existing tool arguments
                                    }
                                },
                                {
                                    "tool_name": "get_file_content",
                                    "tool_args": {
                                        # Your existing tool arguments
                                    }
                                }
                            ]
                            """,
                "items": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "name of actual registered tool you want to call"
                        },
                        "tool_args": {
                            "type": "string",
                            "description": "a dictionary format input arguments for the corresponding registered tool, as it expects"
                        },
                    },
                    "required": ["tool_name", "tool_args"]    
                }
            },
            "max_concurrency": {
                "type": "integer",
                "description": "maximum number of concurrent tools to run",
            },
            "parallel": {
                "type": "boolean",
                "description": "to execute parallely or not",
            },
        },
        "required": ["tools", "max_concurrency", "parallel"],
    },
}