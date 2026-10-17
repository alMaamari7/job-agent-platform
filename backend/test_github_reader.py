

from app.ai.agents.profilling_agent.tools.source_access.readers.github_reader import GitHubReader


reader = GitHubReader()

result = reader.read(
    "https://github.com/alMaamari7/ai-interior-designer-portfolio"
)

print(result[:5000])