from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import (
    GroupMessage,
)
from graia.ariadne.message.chain import (
    MessageChain,
)
from graia.ariadne.message.element import (
    Image,
    Source,
)
from graia.ariadne.message.parser.base import (
    DetectPrefix,
)
from graia.ariadne.util.cooldown import (
    CoolDown,
)
from graia.ariadne.model import Group, Member
from AnimeThesaurus import (
    Talker,
    AnimeThesaurus,
)

from graiax.shortcut.saya import (
    listen,
    dispatch,
    decorate,
)

from rainaa.perm import (
    Allow,
    Ban,
    PermissionDispatcher,
)
from rainaa.tools.text2image import (
    text2image,
)


@listen(GroupMessage)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(Allow("hsochat", ["本群还没开放"])))
@decorate(DetectPrefix("#"))
async def setu(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    member: Member,
    source: Source,
):
    tk = Talker("小霖念", member.name)
    if message.display == "#你会干什么":
        await app.send_group_message(
            group,
            MessageChain(
                Image(
                    data_bytes=await text2image("\n".join(list(AnimeThesaurus.keys())))
                )
            ),
        )
    await app.send_group_message(
        group,
        MessageChain(tk.random_with_replacing(message.display.removeprefix("#"))),
        quote=source,
    )
