from dataclasses import dataclass
from typing import Any


@dataclass
class AgentRunOutput:
    """
    Internal runtime output of a profiling agent.

    Contains the domain-specific result produced by the agent
    together with the exact input snapshot used for the execution.
    """

    result: Any

    input_snapshot: Any | None = None