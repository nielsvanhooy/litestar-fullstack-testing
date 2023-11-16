from litestar.contrib.pydantic import PydanticPlugin
from litestar_aiosql import AiosqlConfig, AiosqlPlugin
from litestar_saq import QueueConfig, SAQConfig, SAQPlugin
from litestar_vite import ViteConfig, VitePlugin

from app.domain.domain_tasks import background_tasks, cron_background_tasks, cron_system_tasks, system_tasks
from app.lib import settings

pydantic = PydanticPlugin(prefer_alias=True)
aiosql = AiosqlPlugin(config=AiosqlConfig())
vite = VitePlugin(
    config=ViteConfig(
        static_dir=settings.STATIC_DIR,
        templates_dir=settings.TEMPLATES_DIR,
        hot_reload=settings.app.DEV_MODE,
        port=3005,
    ),
)


saq = SAQPlugin(
    config=SAQConfig(
        redis_url=settings.redis.URL,
        web_enabled=True,
        worker_processes=1,
        queue_configs=[
            QueueConfig(
                name="system-tasks",
                tasks=system_tasks,
                scheduled_tasks=cron_system_tasks,
            ),
            QueueConfig(
                name="background-tasks",
                tasks=background_tasks,
                scheduled_tasks=cron_background_tasks,
            ),
        ],
    ),
)
