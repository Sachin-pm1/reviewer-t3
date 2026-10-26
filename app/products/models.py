"""ORM models for the products domain.

A **Project** is the top-level workspace (e.g. "Spotify"). It owns one or more
**Products** and a set of **Sources** (configured connectors). Reviews and insights
hang off the project (see the reviews/analysis domains).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Project(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(200), index=True)
    product_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, default=None)

    products: Mapped[list["Product"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    sources: Mapped[list["Source"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))

    project: Mapped[Project] = relationship(back_populates="products")


class Source(Base):
    """A configured data source = a connector type + its config."""

    __tablename__ = "sources"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="configured")
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    last_collected_at: Mapped[datetime | None] = mapped_column(default=None)

    project: Mapped[Project] = relationship(back_populates="sources")
