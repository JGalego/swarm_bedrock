"""
Helper functions
"""

import inspect

from typing import Dict

def function_to_schema(func) -> dict:
    """
    Converts a Python function into a tool spec
    https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-examples.html
    """

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        ) from e

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            ) from e
        parameters[param.name] = {'type': param_type}  # ignoring description

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty  # pylint: disable=protected-access
    ]

    return {
        'toolSpec': {
            'name': func.__name__,
            'description': (func.__doc__ or "").strip(),
            'inputSchema': {
                'json': {
                    'type': "object",
                    'properties': parameters,
                    'required': required
                }
            }
        }
    }

def execute_tool_call(
    tool_call: Dict,
    tools_map: Dict,
    agent_name: str):
    """Executes a single function call."""
    name = tool_call['name']
    args = tool_call['input']

    print(f"\n{agent_name}: {name}({args})")

    # Call corresponding function with provided arguments
    return tools_map[name](**args)
