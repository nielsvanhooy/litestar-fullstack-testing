from dataclasses import dataclass

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.cpe_vendor.models import CPEVendor
from app.lib import dto

__all__ = [
    "CpeVendorDTO",
    "CreateUpdateCPEVendor",
    "CreateUpdateCPEVendorDTO",
]


class CpeVendorDTO(SQLAlchemyDTO[CPEVendor]):
    config = dto.config(
        max_nested_depth=1,
    )


@dataclass
class CreateUpdateCPEVendor:
    name: str | None = None


class CreateUpdateCPEVendorDTO(DataclassDTO[CreateUpdateCPEVendor]):
    """Create CPE."""

    config = dto.config(rename_strategy="lower")
