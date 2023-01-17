import random
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graiax.shortcut.saya import listen, dispatch, decorate
from graia.ariadne.entry import Group, Member, Source, DetectPrefix, At, Plain
from graia.ariadne.util.cooldown import CoolDown
from rainaa.perm import Ban, PermissionDispatcher
import kayaku
from rainaa.config import GPT2Config
import aiohttp


@listen("GroupMessage")
@dispatch(CoolDown(0.7))
@dispatch(PermissionDispatcher(Ban("aichat", ["本群还没开放"])))
async def aichat(
    app: Ariadne, message: MessageChain, group: Group, member: Member, source: Source
):
    cfg = kayaku.create(GPT2Config)
    url = cfg.url
    if url == "":
        await app.send_group_message(group, "机器人还没配置好呢")
        return
    if message.has(At) and message.get(At)[0].target == app.account:
        text = message.include(Plain).display
        async with aiohttp.ClientSession() as s:
            if cfg.global_mode:
                session = 0
            session = group.id
            async with s.get(f"{url}/?session={session}&text={text}") as resp:
                if not resp.status == 200:
                    return
                data = await resp.json()
                await app.send_group_message(group, data["result"],quote=source)
    if str(group.id) not in cfg.group_probability:
        cfg.group_probability[str(group.id)] = 0
        kayaku.save_all()
    text = message.display
    if text == "":
        return
    if str(group.id) not in cfg.group_probability:
        cfg.group_probability[str(group.id)] = 0
        kayaku.save_all()
    probability = cfg.group_probability[str(group.id)]
    if probability == 0:
        return
    if random.randrange(100) > probability:
        return
    async with aiohttp.ClientSession() as s:
        if cfg.global_mode:
            session = 0
        session = group.id
        async with s.get(f"{url}/?session={session}&text={text}") as resp:
            if not resp.status == 200:
                return
            data = await resp.json()
            await app.send_group_message(group, data["result"],quote=source)

@listen("GroupMessage")
@dispatch(CoolDown(0.7))
@dispatch(PermissionDispatcher(Ban("aichat", ["本群还没开放"])))
@decorate(DetectPrefix("设置ai概率"))
async def set_probability(
    app: Ariadne, message: MessageChain, group: Group, member: Member, source: Source
):
    cfg = kayaku.create(GPT2Config)
    text = message.display.removeprefix("设置ai概率")
    if text == "":
        return
    try:
        probability = int(text)
    except Exception:
        await app.send_group_message(group, "概率必须是整数")
        return
    if probability < 0 or probability > 100:
        await app.send_group_message(group, "概率必须在0-100之间")
        return
    cfg.group_probability[str(group.id)] = probability
    kayaku.save_all()
    await app.send_group_message(group, f"设置成功，当前概率为{probability}%")
