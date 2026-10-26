"""Single import point that registers every ORM model on ``Base.metadata``.

``init_models`` imports this so ``create_all`` sees all tables. Keeping the imports in
one place avoids scattering side-effecting imports through the codebase.
"""

from app.analysis.models import ReviewInsightRecord  # noqa: F401
from app.chat.models import ChatSession  # noqa: F401
from app.jobs.models import CollectionJob  # noqa: F401
from app.products.models import Product, Project, Source  # noqa: F401
from app.reports.models import Report  # noqa: F401
from app.reviews.models import Review  # noqa: F401

__all__ = [
    "Project",
    "Product",
    "Source",
    "Review",
    "ReviewInsightRecord",
    "ChatSession",
    "CollectionJob",
    "Report",
]
