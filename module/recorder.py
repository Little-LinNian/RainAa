import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import List

import aiofiles
from arclet.alconna import Alconna, Args, CommandMeta, Option, Subcommand
from arclet.alconna.graia import Match, alcommand, assign
from graia.ariadne.app import Ariadne
from graia.ariadne.entry import Group, GroupMessage, Image, Member, MessageChain, Source,Element
from graia.ariadne.message.element import Forward, ForwardNode
from graia.broadcast.entities.listener import Listener
from rainaa.tools.classes import str_to_class
from loguru import logger
from pydantic import BaseModel

from rainaa.tools.text2image import text2image

alc = Alconna(
    "!rec",
    Option(
        "列出",
        alias=["list"],
        help_text="列出群聊记录",
    ),
    Option(
        "记录",
        alias=["开始", "start", "record"],
        help_text="开始记录群聊记录",
    ),
    Option(
        "结束",
        alias=["停止", "stop", "end", "finish", "close"],
        help_text="停止记录群聊记录",
    ),
    Option(
        "清空",
        alias=["clear"],
        help_text="清空群聊记录",
    ),
    Option(
        "回放",
        Args["reid", int],
        alias=["replay"],
        help_text="回放群聊记录",
    ),
    Subcommand(
        "模式回放",
        alias=["replaywith"],
        help_text="设置回放模式",
        args=Args["reid", int],
        options=[
            Option("谁", alias=["who"], help_text="只回放谁说的话", args=[Args["who", int,0]]),
            Option(
                "类型",
                alias=["type"],
                help_text="只回放某种类型的消息",
                args=[Args["element", str,""]],
            ),
        ],
    ),
    meta=CommandMeta(
        description="群聊记录",
        fuzzy_match=True,
    ),
)


class ChatRecordNode(BaseModel):
    sender: int = 0
    name: str = ""
    message: MessageChain = MessageChain("")
    time: datetime = datetime.now()


class ChatRecord(BaseModel):
    nodes: List[ChatRecordNode] = []


class GroupChatRecord(BaseModel):
    group_chat_record: dict[str, List[ChatRecord]] = {}


@dataclass
class Node:
    listener: Listener
    nodes: List[ChatRecordNode]


sessions: dict[str, Node] = {}

path = pathlib.Path("./cache/group_chat_record.json")
if not path.exists():
    if not pathlib.Path("./cache").exists():
        pathlib.Path("./cache").mkdir()
    path.touch()
    path.write_text(GroupChatRecord().json())


@alcommand(alc, send_error=True)
@assign("列出")
async def list_record(app: Ariadne, msg: MessageChain, group: Group, source: Source):
    async with aiofiles.open(str(path), "r") as f:
        cfg = GroupChatRecord.parse_raw(await f.read())
    gid = str(group.id)
    if gid not in cfg.group_chat_record:
        await app.send_group_message(group, "当前群组没有聊天回放", quote=source)
        return
    record = cfg.group_chat_record[gid]
    if len(record) == 0:
        await app.send_group_message(group, "当前群组没有聊天回放", quote=source)
        return
    records = "当前群组聊天回放列表:\n"
    for i in record:
        records += f"{record.index(i)+1}: {i.nodes[0].time} -- {i.nodes[-1].time}\n"
    await app.send_group_message(
        group, MessageChain(Image(data_bytes=await text2image(records))), quote=source
    )


@alcommand(alc, send_error=True)
@assign("记录")
async def start_record(
    app: Ariadne, msg: MessageChain, group: Group, source: Source, member: Member
):
    gid = str(group.id)
    if gid in sessions:
        await app.send_group_message(group, "当前群组已经在记录聊天回放", quote=source)
        return
    await app.send_group_message(group, "开始记录聊天回放", quote=source)
    bcc = app.broadcast

    async def record(
        app: Ariadne, msg: MessageChain, group: Group, source: Source, member: Member
    ):
        gid = str(group.id)
        if gid not in sessions:
            return
        sessions[gid].nodes.append(
            ChatRecordNode(
                sender=member.id,
                time=datetime.now(),
                message=msg.as_sendable(),
                name=member.name,
            )
        )
        logger.debug(f"record group {gid} message")

    listener = Listener(record, bcc.getDefaultNamespace(), [GroupMessage], [], [])
    bcc.listeners.append(listener)
    sessions[gid] = Node(
        listener,
        [
            ChatRecordNode(
                sender=member.id,
                name=member.name,
                time=datetime.now(),
                message=msg.as_sendable(),
            )
        ],
    )


@alcommand(alc, send_error=True)
@assign("结束")
async def stop_record(app: Ariadne, msg: MessageChain, group: Group, source: Source):
    gid = str(group.id)
    if gid not in sessions:
        await app.send_group_message(group, "当前群组没有在记录聊天回放", quote=source)
        return
    await app.send_group_message(group, "停止记录聊天回放", quote=source)
    bcc = app.broadcast
    bcc.listeners.remove(sessions[gid].listener)
    sessions[gid].nodes.pop(-1)
    async with aiofiles.open(str(path), "r") as f:
        cfg = GroupChatRecord.parse_raw(await f.read())
        if gid not in cfg.group_chat_record:
            cfg.group_chat_record[gid] = []
        cfg.group_chat_record[gid].append(ChatRecord(nodes=sessions[gid].nodes))
        sessions.pop(gid)
    async with aiofiles.open(str(path), "w") as f:
        await f.write(cfg.json())


@alcommand(alc, send_error=True)
@assign("清空")
async def clear_record(app: Ariadne, msg: MessageChain, group: Group, source: Source):
    gid = str(group.id)
    if gid not in sessions:
        await app.send_group_message(group, "当前群组没有在记录聊天回放", quote=source)
        return
    await app.send_group_message(group, "清空聊天回放", quote=source)
    async with aiofiles.open(str(path), "r") as f:
        cfg = GroupChatRecord.parse_raw(await f.read())
        if gid not in cfg.group_chat_record:
            cfg.group_chat_record[gid] = []
        cfg.group_chat_record[gid] = []
    async with aiofiles.open(str(path), "w") as f:
        await f.write(cfg.json())


@alcommand(alc, send_error=True)
@assign("回放")
async def replay_record(
    app: Ariadne, msg: MessageChain, group: Group, source: Source, reid: Match[int]
):
    gid = str(group.id)
    async with aiofiles.open(str(path), "r") as f:
        cfg = GroupChatRecord.parse_raw(await f.read())
    if gid not in cfg.group_chat_record:
        await app.send_group_message(group, "当前群组没有聊天回放", quote=source)
        return
    record = cfg.group_chat_record[gid]
    if len(record) == 0:
        await app.send_group_message(group, "当前群组没有聊天回放", quote=source)
        return
    if reid.result - 1 > len(record):
        await app.send_group_message(group, "当前群组没有这个聊天回放", quote=source)
        return
    record = record[reid.result - 1]
    fowards = [ForwardNode(i.sender, i.time, i.message, i.name) for i in record.nodes]
    # 每 50 条消息分一次包
    for i in range(0, len(fowards), 50):
        await app.send_group_message(
            group, MessageChain([Forward(fowards[i : i + 50])])
        )

@alcommand(alc, send_error=True)
@assign("模式回放")
async def replay_record_moded(
    app: Ariadne, msg: MessageChain, group: Group, source: Source, reid: Match[int],who:Match[int],element:Match[str]
):
    if not who.result and not element.result:
        await app.send_group_message(group, "他奶奶的，你参数呢", quote=source)
        return
    if who.result and  element.result:
        await app.send_group_message(group, "他奶奶的，你怎么那么贪心，想要两根", quote=source)
        return
    gid = str(group.id)
    async with aiofiles.open(str(path), "r") as f:
        cfg: GroupChatRecord = GroupChatRecord.parse_raw(await f.read())
    if gid not in cfg.group_chat_record:
        await app.send_group_message(group, "当前群组没有聊天回放", quote=source)
        return
    record = cfg.group_chat_record[gid]
    if len(record) == 0:
        await app.send_group_message(group, "当前群组没有聊天回放", quote=source)
        return
    if reid.result - 1 > len(record):
        await app.send_group_message(group, "当前群组没有这个聊天回放", quote=source)
        return
    record = record[reid.result - 1]
    fowards = []
    for i in record.nodes:
        if who.result:
            if i.sender == who.result:
                fowards.append(ForwardNode(i.sender, i.time, i.message, i.name))
        elif element.result:
            e= str_to_class(Element,element.result,ignore_high_low=True)
            if element.result in i.message:
                fowards.append(ForwardNode(i.sender, i.time, i.message.include(), i.name))
    # 每 50 条消息分一次包
    for i in range(0, len(fowards), 50):
        await app.send_group_message(
            group, MessageChain([Forward(fowards[i : i + 50])])
        )