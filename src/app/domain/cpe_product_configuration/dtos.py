from dataclasses import dataclass

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.cpe_product_configuration.models import CPEProductConfiguration
from app.lib import dto

__all__ = [
    "CpeProductConfigurationDTO",
]


class CpeProductConfigurationDTO(SQLAlchemyDTO[CPEProductConfiguration]):
    config = dto.config(
        max_nested_depth=1,
    )
