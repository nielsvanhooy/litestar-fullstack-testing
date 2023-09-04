"""Application Modules."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.jwt import OAuth2Login
from litestar.contrib.repository.filters import FilterTypes
from litestar.dto.data_structures import DTOData
from litestar.pagination import OffsetPagination
from litestar.types import TypeEncodersMap
from saq.types import QueueInfo

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
from app.lib import email, settings, worker
from app.lib.service.generic import Service
from app.lib.worker.controllers import WorkerController

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
]

if settings.worker.WEB_ENABLED:
    routes.append(WorkerController)

__all__ = [
    "tasks",
    "scheduled_tasks",
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

system_tasks = [worker.tasks.system_task, worker.tasks.system_upkeep, *domain_system_tasks]

background_tasks = [worker.tasks.background_worker_task, email.send_email, *domain_background_tasks]

ping_tasks = [*domain_ping_tasks]

cron_system_tasks = [
    worker.CronJob(function=worker.tasks.system_upkeep, unique=True, cron="0 * * * *", timeout=500),
    *domain_cron_system_tasks,
]

cron_background_tasks = [
    worker.CronJob(function=worker.tasks.background_worker_task, unique=True, cron="* * * * *", timeout=300),
    *domain_cron_background_tasks,
]

tasks: dict[worker.Queue, list[worker.WorkerFunction]] = {
    worker.queues.get("system-tasks"): system_tasks,  # type: ignore[dict-item]
    worker.queues.get("background-tasks"): background_tasks,  # type: ignore[dict-item]
}
scheduled_tasks: dict[worker.Queue, list[worker.CronJob]] = {
    worker.queues.get("system-tasks"): cron_system_tasks,  # type: ignore[dict-item]
    worker.queues.get("background-tasks"): cron_background_tasks,  # type: ignore[dict-item]
}
ping_task: dict[worker.Queue, list[worker.WorkerFunction]] = {
    worker.queues.get("ping_woker"): ping_tasks, # type: ignore[dict-item]r
}
ping_task_scheduled: dict[worker.Queue, list[worker.CronJob]] = {
    worker.queues.get("ping_worker"): ping_tasks, # type: ignore[dict-item]
}



signature_namespace: Mapping[str, Any] = {
    "Service": Service,
    "FilterTypes": FilterTypes,
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
    "Queue": worker.Queue,
    "QueueInfo": QueueInfo,
    "Job": worker.Job,
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
