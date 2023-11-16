from __future__ import annotations

from typing import Any

from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service import SQLAlchemyAsyncRepositoryService

from .models import CPEVendor

__all__ = ["CPEVendorService", "CPEVendorRepository"]


class CPEVendorRepository(SQLAlchemyAsyncRepository[CPEVendor]):
    """CPE Sqlalchemy Repository"""

    model_type = CPEVendor


class CPEVendorService(SQLAlchemyAsyncRepositoryService[CPEVendor]):
    repository_type = CPEVendorRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: CPEVendorRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type
