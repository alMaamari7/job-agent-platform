from dataclasses import dataclass, field
from typing import Any

from app.ai.agents.profilling_agent.agents.moduls.agent_execution_instance import AgentExecutionInstance


@dataclass
class AgentInstance:
    """
    Represents one persistent profiling-agent instance.

    The same agent instance can be reused across multiple
    executions, for example during review and rework cycles.
    """

    agent_id: str

    agent: Any

    executions: list[AgentExecutionInstance] = field(
        default_factory=list
    )