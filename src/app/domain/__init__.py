"""Application Modules."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.jwt import OAuth2Login
from litestar.dto.data_structures import DTOData
from litestar.pagination import OffsetPagination
from litestar.types import TypeEncodersMap

from app.domain.accounts.dtos import AccountLogin, AccountRegister, UserCreate, UserUpdate
from app.domain.accounts.models import User
from app.domain.analytics.dtos import NewUsersByWeek
from app.domain.cpe.models import CPE
from app.domain.cpe_business_product.models import CPEBusinessProduct
from app.domain.cpe_product_configuration.models import CPEProductConfiguration
from app.domain.cpe_vendor.models import CPEVendor
from app.domain.tags.models import Tag
from app.domain.teams.models import Team
from app.domain.tscm.models import TSCMCheck

from . import (
    accounts,
    analytics,
    cpe,
    cpe_business_product,
    cpe_product_configuration,
    cpe_vendor,
    openapi,
    plugins,
    security,
    ssh_terminal,
    system,
    tags,
    teams,
    tscm,
    urls,
    web,
)
from .domain_tasks import (
    domain_background_tasks,
    domain_cron_background_tasks,
    domain_cron_system_tasks,
    domain_system_tasks,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from litestar.types import ControllerRouterHandler


routes: list[ControllerRouterHandler] = [
    accounts.controllers.AccessController,
    accounts.controllers.AccountController,
    teams.controllers.TeamController,
    # teams.controllers.TeamInvitationController,
    # teams.controllers.TeamMemberController,
    analytics.controllers.StatsController,
    tags.controllers.TagController,
    system.controllers.SystemController,
    web.controllers.WebController,
    cpe.controllers.CpeController,
    cpe_business_product.controllers.CpeBusinessProductController,
    cpe_vendor.controllers.CpeVendorController,
    tscm.controllers.TscmController,
    cpe_product_configuration.controllers.CpeProductConfigurationController,
    ssh_terminal.controllers.SshWebTerminalController,
]

__all__ = [
    "system",
    "accounts",
    "teams",
    "web",
    "cpe",
    "cpe_business_product",
    "cpe_product_configuration",
    "cpe_vendor",
    "tscm",
    "urls",
    "tags",
    "security",
    "routes",
    "openapi",
    "analytics",
    "plugins",
    "signature_namespace",
]


signature_namespace: Mapping[str, Any] = {
    "UUID": UUID,
    "User": User,
    "Team": Team,
    "UserCreate": UserCreate,
    "UserUpdate": UserUpdate,
    "AccountLogin": AccountLogin,
    "AccountRegister": AccountRegister,
    "NewUsersByWeek": NewUsersByWeek,
    "Tag": Tag,
    "OAuth2Login": OAuth2Login,
    "OffsetPagination": OffsetPagination,
    "UserService": accounts.services.UserService,
    "TeamService": teams.services.TeamService,
    "TagService": tags.services.TagService,
    "TeamInvitationService": teams.services.TeamInvitationService,
    "TeamMemberService": teams.services.TeamMemberService,
    "DTOData": DTOData,
    "TypeEncodersMap": TypeEncodersMap,
    "CPE": CPE,
    "CPEService": cpe.services.CPEService,
    "CPEVendor": CPEVendor,
    "CPEVendorService": cpe_vendor.services.CPEVendorService,
    "CPEBusinessProduct": CPEBusinessProduct,
    "CPEBusinessProductService": cpe_business_product.services.CPEBusinessProductService,
    "CPEProductConfiguration": CPEProductConfiguration,
    "CPEProductConfigurationService": cpe_product_configuration.services.CPEProductConfigurationService,
    "TSCMCheck": TSCMCheck,
    "TscmService": tscm.services.TscmService,
}
