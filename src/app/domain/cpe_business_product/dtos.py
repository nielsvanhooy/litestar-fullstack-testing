from dataclasses import dataclass

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.cpe_business_product.models import CPEBusinessProduct
from app.lib import dto

__all__ = [
    "CpeBusinessDTO",
    "CreateCPEBusinessProduct",
    "CreateCpeBusinessProductDTO",
]


class CpeBusinessDTO(SQLAlchemyDTO[CPEBusinessProduct]):
    config = dto.config(
        max_nested_depth=1,
    )


@dataclass
class CreateCPEBusinessProduct:
    name: str
    key: str


class CreateCpeBusinessProductDTO(DataclassDTO[CreateCPEBusinessProduct]):
    """Create CPE."""

    config = dto.config(rename_strategy="lower")


@dataclass
class UpdateCPEBusinessProduct:
    name: str | None = None
    key: str | None = None


class CPEBusinessProductUpdateDTO(DataclassDTO[UpdateCPEBusinessProduct]):
    """User Update."""

    config = dto.config()
