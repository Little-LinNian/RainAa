from arclet.alconna.manager import command_manager
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.cooldown import CoolDown
from graiax.shortcut.saya import decorate, dispatch, listen

from rainaa.tools.text2image import text2image


@listen(GroupMessage)
@dispatch(CoolDown(1.5))
@decorate(MatchContent("小霖念"))
async def setu(
    app: Ariadne,
    group: Group,
    source: Source,
):
    commands = command_manager.all_command_help()
    last_using = command_manager.recent_message
    if not isinstance(last_using, MessageChain):
        last_using = MessageChain("无上一次使用消息记录")
    await app.send_group_message(
        group,
        MessageChain(
            Image(
                data_bytes=await text2image(
                    commands + "\n" + f"上次使用消息记录: {last_using.display}"
                )
            ),
        ),
        quote=source,
    )
