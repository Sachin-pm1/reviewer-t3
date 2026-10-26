"""Base class + registry for report-generating agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.analysis.provider.claude_service import ClaudeService
from app.analysis.schemas import InsightsOverview
from app.core.errors import ValidationError


class ReportAgent(ABC):
    """A single-responsibility agent that turns insights into one document type."""

    report_type: str = ""
    title: str = ""
    schema: type[BaseModel]
    system_prompt: str = ""

    @property
    @abstractmethod
    def task_instruction(self) -> str:
        """The concrete ask appended to the grounded evidence prompt."""

    @abstractmethod
    def render_markdown(self, document: BaseModel, product_name: str) -> str:
        """Deterministically render the structured document to Markdown."""

    async def run(
        self,
        claude: ClaudeService,
        overview: InsightsOverview,
        product_name: str,
        evidence: list[str],
    ) -> tuple[BaseModel, str]:
        """Generate the structured document and its Markdown rendering."""
        user = self._build_user_prompt(overview, product_name, evidence)
        # 4096 was too small once this ran against a real project (858 analyzed
        # reviews) instead of a handful of fixture rows — Claude's output for the
        # nested-list-heavy report schemas (pain points, personas, opportunities,
        # roadmap phases, ...) got cut off mid-JSON and failed to parse. Non-streaming
        # call, so keep it comfortably under the SDK's ~10-minute timeout guard.
        document = await claude.generate(
            system=self.system_prompt, user=user, schema=self.schema, max_tokens=16000
        )
        return document, self.render_markdown(document, product_name)

    def _build_user_prompt(
        self, overview: InsightsOverview, product_name: str, evidence: list[str]
    ) -> str:
        evidence_block = "\n".join(f"- {e}" for e in evidence[:25]) or "(no excerpts)"
        return (
            f"Product: {product_name}\n\n"
            f"Aggregated insights (JSON — ground every claim in this and the excerpts "
            f"below; do not invent facts):\n{overview.model_dump_json(indent=2)}\n\n"
            f"Representative customer feedback excerpts:\n{evidence_block}\n\n"
            f"{self.task_instruction}"
        )


_REGISTRY: dict[str, ReportAgent] = {}


def register_agent(agent: ReportAgent) -> ReportAgent:
    """Register an agent instance under its ``report_type``."""
    if not agent.report_type:
        raise ValueError(f"{type(agent).__name__} must define report_type")
    _REGISTRY[agent.report_type] = agent
    return agent


def available_report_types() -> list[str]:
    return sorted(_REGISTRY)


def get_agent(report_type: str) -> ReportAgent:
    try:
        return _REGISTRY[report_type]
    except KeyError as exc:
        raise ValidationError(
            f"Unknown report type {report_type!r}. "
            f"Available: {', '.join(available_report_types()) or '(none)'}."
        ) from exc


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "_None identified._"
