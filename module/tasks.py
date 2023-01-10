from re import L

from graia.ariadne.event.lifecycle import ApplicationLaunch
from graia.scheduler.timers import every_custom_seconds
from graiax.shortcut.saya import listen, schedule
from loguru import logger

import kayaku


@schedule(every_custom_seconds(10))
def saver():
    kayaku.save_all()
    logger.success("kayaku auto saved!")
