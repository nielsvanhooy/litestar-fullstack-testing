from dataclasses import dataclass

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.tscm.models import TSCMCheck
from app.lib import dto

__all__ = [
    "TscmDTO",
    "CreateTscmCheck",
    "CreateTscmCheckDTO",
    "UpdateTscmCheck",
    "UpdateTscmCheckDTO",
    "PerformTscmCheck",
    "PerformTscmCheckDTO",
]


class TscmDTO(SQLAlchemyDTO[TSCMCheck]):
    config = dto.config(
        max_nested_depth=1,
    )


@dataclass
class CreateTscmCheck:
    key: str
    regex: str
    python_code: str
    remediation_commands: str
    vendor: str
    business_service: str
    device_model: str
    replaces_parent_check: str
    has_child_check: bool
    active: bool


class CreateTscmCheckDTO(DataclassDTO[CreateTscmCheck]):
    """Create CPE."""

    config = dto.config(rename_strategy="lower")


@dataclass
class UpdateTscmCheck:
    key: str | None
    regex: str | None
    python_code: str | None
    remediation_commands: str | None
    vendor: str | None
    business_service: str | None
    device_model: str | None
    replaces_parent_check: str | None
    has_child_check: bool | None
    active: bool | None


class UpdateTscmCheckDTO(DataclassDTO[UpdateTscmCheck]):
    """Update TSCM Check"""

    config = dto.config(rename_strategy="lower")


@dataclass
class PerformTscmCheck:
    device_id: str


class PerformTscmCheckDTO(DataclassDTO[PerformTscmCheck]):
    """Readout CPE."""

    config = dto.config(rename_strategy="lower")
