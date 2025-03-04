from __future__ import annotations

from typing import Any

from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service import SQLAlchemyAsyncRepositoryService

from .models import CPEBusinessProduct

__all__ = ["CPEBusinessProductService", "CPEBusinessProductRepository"]


class CPEBusinessProductRepository(SQLAlchemyAsyncRepository[CPEBusinessProduct]):
    """CPE Sqlalchemy Repository"""

    model_type = CPEBusinessProduct


class CPEBusinessProductService(SQLAlchemyAsyncRepositoryService[CPEBusinessProduct]):
    repository_type = CPEBusinessProductRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: CPEBusinessProductRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type
