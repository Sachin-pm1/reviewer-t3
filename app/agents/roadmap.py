"""Roadmap generator agent — a phased, prioritized product roadmap."""

from __future__ import annotations

from app.agents.base import ReportAgent, _bullets, register_agent
from app.agents.schemas import RoadmapDocument


class RoadmapGeneratorAgent(ReportAgent):
    report_type = "roadmap"
    title = "Product Roadmap"
    schema = RoadmapDocument
    system_prompt = (
        "You are a head of product. Turn aggregated customer-feedback insights into a "
        "phased, prioritized product roadmap. Sequence work by impact and dependency, "
        "assign priorities (P0/P1/P2) and rough effort. Ground initiatives in the evidence."
    )

    @property
    def task_instruction(self) -> str:
        return (
            "Produce a roadmap with a title, a one-paragraph summary, and 3-4 phases. Each "
            "phase has a name, a timeframe (e.g. 'Now', 'Next', 'Later'), objectives, and "
            "prioritized initiatives (title, priority P0/P1/P2, effort low/medium/high)."
        )

    def render_markdown(self, document, product_name: str) -> str:  # type: ignore[override]
        d: RoadmapDocument = document  # type: ignore[assignment]
        lines: list[str] = [f"# {d.title}", f"_Product: {product_name}_", "", d.summary, ""]
        for phase in d.phases:
            lines.append(f"## {phase.phase} ({phase.timeframe})")
            if phase.objectives:
                lines.append("**Objectives:**")
                lines.append(_bullets(phase.objectives))
            lines.append("")
            lines.append("**Initiatives:**")
            for init in phase.initiatives:
                lines.append(f"- `{init.priority}` **{init.title}** _(effort: {init.effort})_")
            if not phase.initiatives:
                lines.append("_None identified._")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


register_agent(RoadmapGeneratorAgent())
