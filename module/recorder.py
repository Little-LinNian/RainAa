from dataclasses import dataclass, field
import pathlib
from re import M
from typing import List
from graiax.shortcut.saya import dispatch
from arclet.alconna import Alconna, Args, Option, CommandMeta
from arclet.alconna.graia import assign, Match, alcommand
from graia.ariadne.app import Ariadne
from loguru import logger
from graia.ariadne.entry import MessageChain, Group, Source, Image, Member, GroupMessage
from graia.ariadne.message.element import Forward, ForwardNode
from graia.broadcast.entities.listener import Listener
from sympy import im
from rainaa.tools.text2image import text2image
from contextvars import ContextVar
import kayaku
import aiofiles
from datetime import datetime
from pydantic import BaseModel


alc = Alconna(
    "!rec",
    Option(
        "列出",
        help_text="列出群聊记录",
    ),
    Option(
        "记录",
        help_text="开始记录群聊记录",
    ),
    Option(
        "结束",
        help_text="停止记录群聊记录",
    ),
    Option(
        "清空",
        help_text="清空群聊记录",
    ),
    Option(
        "回放",
        Args["reid", int],
        help_text="回放群聊记录",
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
async def start_record(app: Ariadne, msg: MessageChain, group: Group, source: Source,member: Member):
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
                sender=member.id, time=datetime.now(), message=msg.as_sendable(),name=member.name
            )
        )
        logger.debug(f"record group {gid} message")

    listener = Listener(record, bcc.getDefaultNamespace(), [GroupMessage], [], [])
    bcc.listeners.append(listener)
    sessions[gid] = Node(listener, [ChatRecordNode(sender=member.id, name=member.name,time=datetime.now(), message=msg.as_sendable())])


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
    fowards = [ForwardNode(i.sender, i.time, i.message,i.name) for i in record.nodes]
    await app.send_group_message(group, MessageChain([Forward(fowards)]))
