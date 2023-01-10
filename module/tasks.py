import json
from re import L

from graia.ariadne.app import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunch
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.scheduler.timers import every_custom_seconds
from graiax.shortcut.saya import listen, schedule
from loguru import logger

import kayaku
from rainaa.tools.text2image import text2image


@schedule(every_custom_seconds(10))
def saver():
    kayaku.save_all()
    logger.success("kayaku auto saved!")


@listen(ApplicationLaunch)
async def app_launch(app: Ariadne):
    with open("rdb_message.json") as f:
        if f.read():
            f.seek(0)
            data = json.load(f)
            await app.send_group_message(
                data["source"],
                MessageChain(Image(data_bytes=await text2image(data["message"]))),
            )
            with open("rdb_message.json", "w") as f:
                f.write("")
