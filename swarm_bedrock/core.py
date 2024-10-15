# pylint: disable=too-few-public-methods
"""
Core - Swarms
"""

# Standard imports
from abc import ABC, abstractmethod
from typing import List

# Package imports
import boto3

# Local imports
from .types import (
    Agent,
    Response
)
from .util import (
    function_to_schema,
    execute_tool_call
)

class Swarm(ABC):
    """Base Swarm class"""

    @abstractmethod
    def run(
        self,
        agent: Agent,
        messages: List):
        """Runs a full turn of the swarm routine."""


class BedrockSwarm(Swarm):
    """Swarm class with Amazon Bedrock Converse API support"""
    def __init__(self, client=None):
        if not client:
            client = boto3.client('bedrock-runtime')
        self.client = client

    def run(self, agent, messages):

        current_agent = agent
        num_init_messages = len(messages)
        messages = messages.copy()

        while True:

            # Turn Python functions into tools and save a reverse map
            tool_config = {'tools': [function_to_schema(tool) for tool in current_agent.tools]}
            tools_map = {tool.__name__: tool for tool in current_agent.tools}

            # === 1. Call Converse API ===

            response = self.client.converse(
                modelId=current_agent.model,
                system=[{'text': current_agent.instructions}],
                messages=messages,
                inferenceConfig=current_agent.inference_config,
                toolConfig=tool_config or None
            )
            output_message = response['output']['message']
            messages.append(output_message)
            stop_reason = response['stopReason']

            if 'text' in output_message['content'][0]:
                print(f"\n{current_agent.name}: {output_message['content'][0]['text']}")

            # === 2. Handle tool calls ===

            if stop_reason == "tool_use":
                tool_requests = [m for m in output_message['content'] if 'toolUse' in m]
                for tool_request in tool_requests:
                    # Call tool
                    tool_use = tool_request['toolUse']
                    result = execute_tool_call(tool_use, tools_map, current_agent.name)

                    # Transfer to a different agent
                    if isinstance(result, Agent):
                        current_agent = result
                        result = {
                            'message': f"Transferred to {agent.name}. Adopt persona immediately."
                        }

                    # Process result
                    result_message = {
                        'role': "user",
                        'content': [{
                            'toolResult': {
                                'toolUseId': tool_use['toolUseId'],
                                'content': [{
                                    'json': result
                                }]
                            }
                        }]
                    }
                    messages.append(result_message)
            else:
                break

        # ==== 3. Return current agent and new messages =====

        return Response(agent=current_agent, messages=messages[num_init_messages:])
