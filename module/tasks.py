from re import L
from graiax.shortcut.saya import (
    schedule,
    listen,
)
from graia.scheduler.timers import (
    every_custom_seconds,
)
from graia.ariadne.event.lifecycle import (
    ApplicationLaunch,
)
import kayaku
from loguru import logger


@schedule(every_custom_seconds(10))
def saver():
    kayaku.save_all()
    logger.success("kayaku auto saved!")
