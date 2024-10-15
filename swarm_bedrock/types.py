"""
Types - Agents & Responses
"""

from typing import Dict, Optional
from pydantic import BaseModel

class Agent(BaseModel):
    """
    Basic Agent class
    """
    name: str = "Agent"
    instructions: str = "You are a helpful agent"
    model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    inference_config: Dict = {}
    tools: list = []  # TODO: refactor to handle 'no tools' case

class Response(BaseModel):
    """
    Encapsulates the possible return values for an agent function.
    """
    agent: Optional[Agent]
    messages: list
