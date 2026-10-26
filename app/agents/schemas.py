"""Structured output schemas for the generator agents.

Kept structured-output friendly: enums via ``Literal``, nested object lists, no exotic
constraints. These are the contracts Claude fills — the generated documents are
validated against them, never accepted as free-form text.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Impact = Literal["low", "medium", "high"]
Effort = Literal["low", "medium", "high"]
Severity = Literal["low", "medium", "high", "critical"]
Priority = Literal["P0", "P1", "P2"]


# --- Executive report ---
class PainPointItem(BaseModel):
    label: str
    evidence_summary: str
    severity: Severity


class PersonaItem(BaseModel):
    name: str
    description: str
    key_needs: list[str] = Field(default_factory=list)


class OpportunityItem(BaseModel):
    title: str
    rationale: str
    impact: Impact
    effort: Effort


class RoadmapPhase(BaseModel):
    phase: str
    focus: str
    items: list[str] = Field(default_factory=list)


class ExecutiveReport(BaseModel):
    executive_summary: str
    problem_statement: str
    validated_pain_points: list[PainPointItem] = Field(default_factory=list)
    personas: list[PersonaItem] = Field(default_factory=list)
    jobs_to_be_done: list[str] = Field(default_factory=list)
    root_cause_analysis: str
    business_impact: str
    opportunity_ranking: list[OpportunityItem] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    recommended_mvp: str
    product_roadmap: list[RoadmapPhase] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


# --- PRD ---
class UserStory(BaseModel):
    as_a: str
    i_want: str
    so_that: str


class PRDDocument(BaseModel):
    title: str
    overview: str
    goals: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    user_stories: list[UserStory] = Field(default_factory=list)
    functional_requirements: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


# --- Roadmap ---
class Initiative(BaseModel):
    title: str
    priority: Priority
    effort: Effort


class RoadmapStage(BaseModel):
    phase: str
    timeframe: str
    objectives: list[str] = Field(default_factory=list)
    initiatives: list[Initiative] = Field(default_factory=list)


class RoadmapDocument(BaseModel):
    title: str
    summary: str
    phases: list[RoadmapStage] = Field(default_factory=list)
