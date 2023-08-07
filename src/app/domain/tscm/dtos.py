from dataclasses import dataclass

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.tscm.models import TSCMCheck
from app.lib import dto

__all__ = [
    "TscmDTO",
    "CreateTscmCheck",
    "CreateTscmCheckDTO"
]


class TscmDTO(SQLAlchemyDTO[TSCMCheck]):
    config = dto.config(
        max_nested_depth=0,
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
