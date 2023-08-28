from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any

from app.lib import settings

__all__ = ["ElasticSearchRepository"]


class AbstractDataExportRepository(metaclass=ABCMeta):
    """Interface for persistent data exporting to external sources
    For now Elasticsearch
    """

    @abstractmethod
    async def add(self, data: dict) -> None:
        """Add ``data`` to the collection.

        Args:
            data: Instance to be added to the collection.

        Returns:
            The added instance.
        """


class ElasticSearchRepository(AbstractDataExportRepository):
    def __init__(self, test_run: bool = False) -> None:
        self.test_run = test_run
        self.elasticsearch_session = settings.elasticsearch_session

    async def add(self, data: Any) -> None:
        try:
            if settings.elasticsearch.AVAILABLE and self.test_run is False:
                await self.elasticsearch_session.index(**data)
        except Exception:
            pass
