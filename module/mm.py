from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import (
    Image,
)
from graia.ariadne.message.chain import (
    MessageChain,
)
from creart import it
from graia.ariadne.model import Group
from graia.ariadne.message.element import (
    At,
    Image,
)
from graiax.shortcut.saya import dispatch
from graia.saya import Saya
import kayaku
from rainaa.config import (
    BotConfig,
    MiraiConfig,
    SayaConfig,
)
from rainaa.perm import (
    MasterPermission,
    PermissionDispatcher,
)
from rainaa.tools.text2image import (
    text2image,
)
from arclet.alconna import (
    Alconna,
    Args,
    Option,
    CommandMeta,
)
from arclet.alconna.graia import (
    assign,
    Match,
    alcommand,
)

module_control = Alconna(
    "!模块",
    Option(
        "列出",
        Args["spec;?", At],
        alias=["list"],
    ),
    Option(
        "卸载",
        Args[
            "path",
            str,
        ],
        alias=["关闭", "uninstall"],
        help_text="卸载一个模块",
    ),
    Option(
        "安装",
        Args[
            "path",
            str,
        ],
        alias=["开启", "install"],
        help_text="安装一个模块",
    ),
    Option(
        "禁用",
        Args[
            "path",
            str,
        ]["spec;?", At],
        alias=["disable"],
        help_text="禁用一个模块",
    ),
    Option(
        "启用",
        Args[
            "path",
            str,
        ]["spec;?", At],
        alias=["enable"],
        help_text="启用一个模块",
    ),
    Option(
        "重载",
        Args[
            "path",
            str,
        ],
        alias=["重启", "reload"],
        help_text="重新载入一个模块",
    ),
    meta=CommandMeta(
        "管理机器人的模块",
        example="$模块 列出\n$模块 卸载 setu",
    ),
)


@alcommand(module_control, send_error=True)
# @mention("spec")
@assign("列出")
@dispatch(PermissionDispatcher(MasterPermission()))
async def _m_list(app: Ariadne, group: Group):
    saya = it(Saya)
    cfg = kayaku.create(BotConfig)
    qid = kayaku.create(MiraiConfig).account
    scfg = kayaku.create(SayaConfig)
    md = f"""
{cfg.bot_name} ({qid}) 模块信息
| 模块名 | 模块路径 | 状态 |
| ----- | ------- | --- |
"""
    for (
        path,
        channel,
    ) in saya.channels.items():
        md += f"| {channel.meta['name'] or path.split('.')[-1]} | {path} | √ 已安装 |\n"
    for path in scfg.deprecated_modules:
        md += f"| { path.split('.')[-1]} | {path} | × 已停用 |\n"

    return await app.send_message(
        group,
        MessageChain(Image(data_bytes=await text2image(md))),
    )


@alcommand(module_control, send_error=True)
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("卸载")
async def _m_uninstall(
    app: Ariadne,
    group: Group,
    path: Match[str],
):
    saya = it(Saya)
    cfg = kayaku.create(SayaConfig)
    channel_path = path.result if path.available else "mm"
    if channel_path.split(".")[-1] == "mm":
        return await app.send_message(group, MessageChain("无法卸载管理模块"))
    if not (_channel := saya.channels.get(channel_path)):
        return await app.send_message(
            group,
            MessageChain("该模组未安装, 您可能需要安装它"),
        )
    try:
        saya.uninstall_channel(_channel)
    except Exception as e:
        await app.send_message(
            group,
            MessageChain(f"卸载 {channel_path} 失败！"),
        )
        raise e
    else:
        cfg.deprecated_modules.append(channel_path)
        return await app.send_message(
            group,
            MessageChain(f"卸载 {channel_path} 成功"),
        )


@alcommand(module_control, send_error=True)
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("安装")
async def _m_install(
    app: Ariadne,
    group: Group,
    path: Match[str],
):
    saya = it(Saya)
    channel_path = path.result if path.available else "mm"
    if channel_path.split(".")[-1] == "mm":
        return
    if channel_path in saya.channels:
        return await app.send_message(group, MessageChain("该模组已安装"))
    try:
        with saya.module_context():
            saya.require(channel_path)
    except Exception as e:
        await app.send_message(
            group,
            MessageChain(f"安装 {channel_path} 失败！"),
        )
        raise e
    else:
        return await app.send_message(
            group,
            MessageChain(f"安装 {channel_path} 成功"),
        )


@alcommand(module_control, send_error=True)
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("重载")
async def _m_reload(
    app: Ariadne,
    group: Group,
    path: Match[str],
):
    saya = it(Saya)
    cfg = kayaku.create(SayaConfig)
    channel_path = path.result if path.available else "mm"
    if channel_path.split(".")[-1] == "mm":
        return

    if not (_channel := saya.channels.get(channel_path)):
        return await app.send_message(
            group,
            MessageChain("该模组未安装, 您可能需要安装它"),
        )
    try:
        saya.uninstall_channel(_channel)
    except Exception as e:
        await app.send_message(
            group,
            MessageChain(f"重载 {channel_path} 过程中卸载失败！"),
        )
        raise e
    try:
        with saya.module_context():
            saya.require(channel_path)
    except Exception as e:
        await app.send_message(
            group,
            MessageChain(f"重载 {channel_path} 过程中安装失败！"),
        )
        raise e
    else:
        return await app.send_message(
            group,
            MessageChain(f"重载 {channel_path} 成功"),
        )
