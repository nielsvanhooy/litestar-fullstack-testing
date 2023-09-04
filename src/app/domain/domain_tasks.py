from collections.abc import Callable

from app.domain import cpe
from app.lib import worker

domain_system_tasks: list = []

domain_background_tasks: list[Callable] = [
    cpe.business_logic.communicate_with_cpe,
    cpe.business_logic_ping._ping,
]

domain_ping_tasks: list[Callable] = []

domain_cron_system_tasks: list = []

domain_cron_background_tasks: list = [
    worker.CronJob(function=cpe.business_logic_ping.ping_cpes, unique=True, cron="* * * * *", timeout=300),
]
