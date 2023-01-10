import datetime
import json
import random

from aiohttp import ClientSession
from arclet.alconna import Alconna, Args, CommandMeta, Option
from arclet.alconna.graia import Match, alcommand, assign
from graia.ariadne.app import Ariadne
from graia.ariadne.entry import Group, MessageChain, Source
from graia.ariadne.message.element import Forward, ForwardNode, Image

# thanks to https://docs.tenapi.cn/
alc = Alconna(
    ["!短视频", "！短视频", "短视频"],
    Args["main_args", str],
    Option("--图集视频"),
    separators=[" ", ""],
    meta=CommandMeta(
        "短视频下载",
        example="!短视频 https://v.douyin.com/JVd6Jh/",
        fuzzy_match=True,
    ),
)


@alcommand(alc, send_error=True)
@assign("$main")
async def function(
    app: Ariadne,
    group: Group,
    msg: MessageChain,
    source: Source,
    main_args: Match[str],
):
    share_link = main_args.result
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76"
    }
    await app.send_group_message(group, "正在解析短视频")
    async with ClientSession(headers=header) as s:
        async with s.get(f"https://tenapi.cn/v2/video?url={share_link}") as share:
            data = json.loads(await share.text())
            if data["code"] != 200:
                await app.send_group_message(
                    group,
                    data["msg"],
                    quote=source,
                )
                return
            await app.send_group_message(
                group,
                f"短视频解析完成\n{data['data']['url']}",
            )


@alcommand(alc, send_error=True)
@assign("图集视频")
async def simages(
    app: Ariadne,
    group: Group,
    msg: MessageChain,
    source: Source,
    main_args: Match[str],
):
    share_link = main_args.result
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76"
    }
    await app.send_group_message(group, "正在解析图集视频")
    async with ClientSession(headers=header) as s:
        async with s.get(f"https://tenapi.cn/v2/images?url={share_link}") as share:
            data = json.loads(await share.text())
            if data["code"] != 200:
                await app.send_group_message(
                    group,
                    data["msg"],
                    quote=source,
                )
                return
            fwds = []
            for i in data["data"]["images"]:
                fwds.append(
                    ForwardNode(
                        target=random.choice(await app.get_member_list(group)),
                        time=datetime.datetime.now(),
                        message=MessageChain(Image(url=i)),
                    )
                )
            await app.send_group_message(group, "图片合集短视频解析完成")
            await app.send_group_message(
                group,
                MessageChain(Forward(fwds)),
            )
