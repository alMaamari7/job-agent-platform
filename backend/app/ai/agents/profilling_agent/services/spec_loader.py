from pathlib import Path


class AgentSpecLoader:

    def __init__(self, agent_dir: Path):
        self.agent_dir = agent_dir

    def _load(self, filename: str) -> str:
        path = self.agent_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Agent specification not found: {path}"
            )

        return path.read_text(
            encoding="utf-8"
        )

    def load_identity(self) -> str:
        return self._load("identity.md")

    def load_instructions(self) -> str:
        return self._load("instructions.md")

    def load_workflow(self) -> str:
        return self._load("workflow.md")

    def load_contract(self) -> str:
        return self._load("contract.md")

    def load_all(self) -> str:
        return "\n\n".join(
            [
                "# IDENTITY",
                self.load_identity(),
                "# INSTRUCTIONS",
                self.load_instructions(),
                "# WORKFLOW",
                self.load_workflow(),
                "# CONTRACT",
                self.load_contract(),
            ]
        )