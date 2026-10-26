"""PRD generator agent — a product requirements document for the top opportunity."""

from __future__ import annotations

from app.agents.base import ReportAgent, _bullets, register_agent
from app.agents.schemas import PRDDocument


class PRDGeneratorAgent(ReportAgent):
    report_type = "prd"
    title = "Product Requirements Document"
    schema = PRDDocument
    system_prompt = (
        "You are a senior product manager. From aggregated customer-feedback insights, "
        "write a focused PRD for the single highest-impact opportunity. Be concrete and "
        "implementable. Derive goals, user stories, and requirements from the evidence; "
        "do not invent unrelated scope."
    )

    @property
    def task_instruction(self) -> str:
        return (
            "Identify the highest-impact opportunity from the insights and write a PRD for "
            "it: a clear title, overview, goals, non-goals, user stories (as a / I want / "
            "so that), functional requirements, success metrics, and open questions."
        )

    def render_markdown(self, document, product_name: str) -> str:  # type: ignore[override]
        d: PRDDocument = document  # type: ignore[assignment]
        lines: list[str] = [f"# PRD: {d.title}", f"_Product: {product_name}_", ""]
        lines += ["## Overview", "", d.overview, ""]
        lines += ["## Goals", "", _bullets(d.goals), ""]
        lines += ["## Non-Goals", "", _bullets(d.non_goals), ""]

        lines += ["## User Stories", ""]
        for s in d.user_stories:
            lines.append(f"- As a **{s.as_a}**, I want **{s.i_want}**, so that {s.so_that}.")
        if not d.user_stories:
            lines.append("_None identified._")
        lines.append("")

        lines += ["## Functional Requirements", "", _bullets(d.functional_requirements), ""]
        lines += ["## Success Metrics", "", _bullets(d.success_metrics), ""]
        lines += ["## Open Questions", "", _bullets(d.open_questions), ""]
        return "\n".join(lines).strip() + "\n"


register_agent(PRDGeneratorAgent())
