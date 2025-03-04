from dataclasses import dataclass

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.cpe.models import CPE
from app.lib import dto

__all__ = [
    "CpeDTO",
    "CreateCPE",
    "CreateCpeDTO",
    "ReadoutCPE",
    "ReadoutCpeDTO",
    "UpdateCPE",
    "CPEUpdateDTO",
]


class CpeDTO(SQLAlchemyDTO[CPE]):
    config = dto.config(
        exclude={
            "id",
        },
        max_nested_depth=1,
    )


@dataclass
class CreateCPE:
    device_id: str
    routername: str
    os: str
    mgmt_ip: str
    vendor: str
    business_service: str
    product_configuration: int
    sec_mgmt_ip: str | None = None
    online_status: bool = False


class CreateCpeDTO(DataclassDTO[CreateCPE]):
    """Create CPE."""

    config = dto.config(rename_strategy="lower")


@dataclass
class ReadoutCPE:
    device_id: str


class ReadoutCpeDTO(DataclassDTO[ReadoutCPE]):
    """Readout CPE."""

    config = dto.config(rename_strategy="lower")


@dataclass
class UpdateCPE:
    device_id: str | None = None
    routername: str | None = None
    os: str | None = None
    mgmt_ip: str | None = None
    sec_mgmt_ip: str | None = None
    online_status: bool | None = None
    vendor: str | None = None
    business_service: str | None = None
    product_configuration: int | None = None


class CPEUpdateDTO(DataclassDTO[UpdateCPE]):
    """User Update."""

    config = dto.config(rename_strategy="lower")
