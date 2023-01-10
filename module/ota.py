import json

from arclet.alconna import Alconna, Args, CommandMeta, Option
from arclet.alconna.graia import Match, alcommand, assign
from creart import it
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.model import Group
from graia.saya import Saya
from graiax.shortcut.saya import dispatch

import kayaku
from rainaa.config import BotConfig, MiraiConfig, SayaConfig
from rainaa.perm import MasterPermission, PermissionDispatcher
from rainaa.tools.text2image import text2image

rdb_alc = Alconna(
    "!rdb",
    Option(
        "reboot",
        Args["partition", str, "system"],
        alias=["重启"],
        help_text="重启 Rainaa",
    ),
    Option(
        "shutdown",
        alias=["关机"],
        help_text="关闭 Rainaa",
    ),
    Option(
        "ota",
        Args[
            "url",
            str,
            "https://gh.api.99988866.xyz/https://github.com/Little-LinNian/RainAa/archive/master.zip",
        ],
        alias=["更新"],
        help_text="更新 Rainaa, 默认源为主仓库镜像 https://gh.api.99988866.xyz/https://github.com/Little-LinNian/RainAa/archive/master.zip",
    ),
    meta=CommandMeta(
        description="Rainaa Developer Bridge",
        fuzzy_match=True,
    ),
)


@alcommand(rdb_alc, send_error=True)
@assign("reboot")
@dispatch(PermissionDispatcher(MasterPermission()))
async def rdb_reboot(
    app: Ariadne,
    group: Group,
    partition: Match[str],
):
    with open("rdb_interface.json", "w") as f:
        json.dump(
            {
                "command": "reboot",
                "partition": partition.result,
            },
            f,
        )
        await app.send_group_message(
            group,
            "Rainaa 已经向 RDB 发送了重启指令",
        )


@alcommand(rdb_alc, send_error=True)
@assign("shutdown")
@dispatch(PermissionDispatcher(MasterPermission()))
async def rdb_shutdown(
    app: Ariadne,
    group: Group,
):
    with open("rdb_interface.json", "w") as f:
        json.dump(
            {
                "command": "shutdown",
            },
            f,
        )
        await app.send_group_message(
            group,
            "Rainaa 已经向 RDB 发送了关机指令",
        )


@alcommand(rdb_alc, send_error=True)
@assign("ota")
@dispatch(PermissionDispatcher(MasterPermission()))
async def rdb_ota(
    app: Ariadne,
    group: Group,
    url: Match[str],
):
    with open("rdb_interface.json", "w") as f:
        json.dump(
            {
                "command": "ota",
                "url": url.result,
                "source": group.id,
            },
            f,
        )
        await app.send_group_message(
            group,
            "Rainaa 已经向 RDB 发送了更新指令",
        )
