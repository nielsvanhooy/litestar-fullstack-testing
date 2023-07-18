from app.domain import cpe

domain_system_tasks = []

domain_background_tasks = [
    cpe.business_logic.communicate_with_cpe,
]

domain_cron_system_tasks = []

domain_cron_background_tasks = []
