from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any

from elasticsearch.helpers import async_bulk

from app.lib import log, settings

__all__ = ["ElasticSearchRepository"]

logger = log.get_logger()


class AbstractDataExportRepository(metaclass=ABCMeta):
    """Interface for persistent data exporting to external sources
    For now Elasticsearch
    """

    @abstractmethod
    async def add(self, **kwargs: Any) -> None:
        """Add ``data`` to the collection.

        Args:
            **kwargs: keyworded arguments to be passed to data export

        Returns:
            The added instance.
        """

    @abstractmethod
    async def bulk(self, **kwargs: Any) -> None:
        """Add data in bulk to the collection

        Args:
            **kwargs: keyworded arguments to be passed to data export

        """


class ElasticSearchRepository(AbstractDataExportRepository):
    def __init__(self, test_run: bool = False) -> None:
        self.test_run = test_run
        self.elasticsearch_session = settings.elasticsearch_session

    async def add(self, **kwargs: Any) -> None:
        try:
            if settings.elasticsearch.AVAILABLE and self.test_run is False:
                await self.elasticsearch_session.index(**kwargs)
        except Exception:
            pass

    async def bulk(self, **kwargs: Any) -> None:
        await async_bulk(self.elasticsearch_session, kwargs.get("iterator"))
