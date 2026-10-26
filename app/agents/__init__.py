"""AI agents that synthesize insights into executive-ready documents.

Each agent has a single responsibility (an executive report, a PRD, a roadmap),
consumes the aggregated insights as grounded evidence, and produces a schema-validated
document via ``ClaudeService``. New agents register themselves, so the report catalog
grows without touching the reports domain.
"""

from app.agents import executive, prd, roadmap  # noqa: F401 - registers agents

__all__ = ["executive", "prd", "roadmap"]
