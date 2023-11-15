from dataclasses import dataclass

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.cpe_product_configuration.models import CPEProductConfiguration
from app.lib import dto

__all__ = [
    "CpeProductConfigurationDTO",
    "CreateCpeProductConfigurationDTO",
    "UpdateCPEProductConfiguration",
    "CreateCPEProductConfiguration",
    "CPEProductConfigurationUpdateDTO",
]


class CpeProductConfigurationDTO(SQLAlchemyDTO[CPEProductConfiguration]):
    config = dto.config(
        max_nested_depth=1,
    )


@dataclass
class CreateCPEProductConfiguration:
    description: str
    configuration_id: int
    cpe_model: str
    vendor: str


class CreateCpeProductConfigurationDTO(DataclassDTO[CreateCPEProductConfiguration]):
    """Create CPE."""

    config = dto.config(rename_strategy="lower")


@dataclass
class UpdateCPEProductConfiguration:
    description: str | None = None
    configuration_id: int | None = None
    cpe_model: str | None = None
    vendor: str | None = None


class CPEProductConfigurationUpdateDTO(DataclassDTO[UpdateCPEProductConfiguration]):
    """User Update."""

    config = dto.config(rename_strategy="lower")
