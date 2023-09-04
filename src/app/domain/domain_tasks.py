from collections.abc import Callable

from app.domain import cpe

domain_system_tasks: list = []

domain_background_tasks: list[Callable] = [
    cpe.business_logic.communicate_with_cpe,
]

domain_ping_tasks: list[Callable] = [
    cpe.business_logic_ping.ping_cpes,
]

domain_cron_system_tasks: list = []

domain_cron_background_tasks: list = []
