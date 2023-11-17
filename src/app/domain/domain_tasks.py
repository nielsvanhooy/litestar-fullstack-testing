from litestar_saq import CronJob

from app.domain.system import tasks
from app.lib import email

from . import cpe

# TASKS ###

# All the domain tasks you want to add ##
domain_system_tasks: list = []
domain_cron_system_tasks: list = []


domain_background_tasks: list = [
    cpe.business_logic.communicate_with_cpe,
    cpe.business_logic_ping._ping,
]
domain_cron_background_tasks: list = [
    CronJob(function=cpe.business_logic_ping.ping_cpes, unique=True, cron="* * * * *", timeout=300),
]


# Unpacking of all the tasks to the workers

system_tasks = [tasks.system_task, tasks.system_upkeep, *domain_system_tasks]
background_tasks = [tasks.background_worker_task, email.send_email, *domain_background_tasks]

# CRON
cron_system_tasks = [
    CronJob(function=tasks.system_upkeep, unique=True, cron="0 * * * *", timeout=500),
    *domain_cron_system_tasks,
]

cron_background_tasks = [
    CronJob(function=tasks.background_worker_task, unique=True, cron="* * * * *", timeout=300),
    *domain_cron_background_tasks,
]
