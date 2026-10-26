"""Executive report agent — the full product-intelligence readout."""

from __future__ import annotations

from app.agents.base import ReportAgent, _bullets, register_agent
from app.agents.schemas import ExecutiveReport


class ExecutiveReportAgent(ReportAgent):
    report_type = "executive"
    title = "Executive Product Intelligence Report"
    schema = ExecutiveReport
    system_prompt = (
        "You are a principal product strategist. Synthesize aggregated customer-feedback "
        "insights into an executive-ready report for a product leadership team. Be "
        "specific, evidence-driven, and decisive. Rank opportunities by impact vs. effort. "
        "Ground every claim in the provided insights and excerpts; do not fabricate metrics."
    )

    @property
    def task_instruction(self) -> str:
        return (
            "Produce the executive report: a crisp executive summary, the core problem "
            "statement, validated pain points, personas, jobs-to-be-done, root-cause "
            "analysis, business impact, a ranked opportunity list, success metrics, a "
            "recommended MVP, a phased product roadmap, key risks, and concrete "
            "recommendations."
        )

    def render_markdown(self, document, product_name: str) -> str:  # type: ignore[override]
        r: ExecutiveReport = document  # type: ignore[assignment]
        lines: list[str] = [f"# {self.title}: {product_name}", ""]

        lines += ["## Executive Summary", "", r.executive_summary, ""]
        lines += ["## Problem Statement", "", r.problem_statement, ""]

        lines += ["## Validated Pain Points", ""]
        for pp in r.validated_pain_points:
            lines.append(f"- **{pp.label}** _(severity: {pp.severity})_ — {pp.evidence_summary}")
        lines.append("")

        lines += ["## Personas", ""]
        for p in r.personas:
            lines.append(f"### {p.name}")
            lines.append(p.description)
            if p.key_needs:
                lines.append("Key needs:")
                lines.append(_bullets(p.key_needs))
            lines.append("")

        lines += ["## Jobs To Be Done", "", _bullets(r.jobs_to_be_done), ""]
        lines += ["## Root Cause Analysis", "", r.root_cause_analysis, ""]
        lines += ["## Business Impact", "", r.business_impact, ""]

        lines += ["## Opportunity Ranking", ""]
        for o in r.opportunity_ranking:
            lines.append(
                f"- **{o.title}** _(impact: {o.impact}, effort: {o.effort})_ — {o.rationale}"
            )
        lines.append("")

        lines += ["## Success Metrics", "", _bullets(r.success_metrics), ""]
        lines += ["## Recommended MVP", "", r.recommended_mvp, ""]

        lines += ["## Product Roadmap", ""]
        for phase in r.product_roadmap:
            lines.append(f"### {phase.phase} — {phase.focus}")
            lines.append(_bullets(phase.items))
            lines.append("")

        lines += ["## Risks", "", _bullets(r.risks), ""]
        lines += ["## Recommendations", "", _bullets(r.recommendations), ""]
        return "\n".join(lines).strip() + "\n"


register_agent(ExecutiveReportAgent())
