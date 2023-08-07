from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO

from app.domain.tscm.models import TSCMCheck
from app.lib import dto

__all__ = [
    "TscmDTO",
]


class TscmDTO(SQLAlchemyDTO[TSCMCheck]):
    config = dto.config(
        max_nested_depth=0,
    )
