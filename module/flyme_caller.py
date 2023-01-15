from arclet.alconna import Args, CommandMeta
from arclet.alconna.graia import Alconna, Match, alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.entry import MessageEvent

alc = Alconna(
    "!fc",
    Args["main_args", int, 3],
    meta=CommandMeta(
        description="红包助手 用户召唤器",
        usage="!fc 6",
    ),
)


@alcommand(alc)
async def flyme_caller(app: Ariadne, main_args: Match[int], event: MessageEvent):
    if main_args.result > 10:
        await app.send_group_message(event, "召唤次数不能超过10次")
        return
    for i in range(main_args.result):
        await app.send_group_message(event, "[QQ红包]")
