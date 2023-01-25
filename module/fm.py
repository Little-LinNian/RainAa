from arclet.alconna import Alconna, Args, CommandMeta, Option, Subcommand
from arclet.alconna.graia import Match, alcommand, assign
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.util.cooldown import CoolDown
from graiax.shortcut.saya import dispatch

import kayaku
from rainaa.config import AllowList, BanList
from rainaa.perm import MasterPermission, PermissionDispatcher

alc = Alconna(
    "!功能",
    Subcommand(
        "放行",
        options=[
            Option(
                "群组",
                Args["gid", int],
                help_text="放行某个群组使用此功能",
            ),
            Option(
                "个人",
                Args["id", int],
                help_text="放行某个个人使用此功能",
            ),
            Option(
                "群员",
                Args["gid", int]["id", int],
                help_text="放行某个群组的某个成员使用此功能",
            ),
        ],
    ),
    Subcommand(
        "ban",
        options=[
            Option(
                "群组",
                Args["gid", int],
                help_text="阻止某个群组使用此功能",
            ),
            Option(
                "个人",
                Args["id", int],
                help_text="阻止某个个人使用此功能",
            ),
            Option(
                "群员",
                Args["gid", int]["id", int],
                help_text="阻止某个群组的某个成员使用此功能",
            ),
        ],
    ),
    Args["main_args", str]["re", bool, False],
    meta=CommandMeta(
        "管理功能权限",
        example="#功能 ban 群组 114514",
        fuzzy_match=True,
    ),
)


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("放行.群组")
async def fgp(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    member: Member,
    re: Match[bool],
    gid: Match[int],
    main_args: Match[str],
):
    if not gid.available and main_args.available:
        return
    allowlist = kayaku.create(AllowList)
    if main_args.result not in allowlist.allow_group:
        await app.send_group_message(group, "哪来的功能，没这玩意")
        return
    if re.result:
        allowlist.allow_group[main_args.result].remove(gid.result)
        await app.send_group_message(
            group,
            f"已撤销 {gid.result} 的 {main_args.result} 访问权",
        )
        return
    allowlist.allow_group[main_args.result].append(gid.result)
    await app.send_group_message(
        group,
        f"已授权 {gid.result} 的 {main_args.result} 访问权",
    )


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("放行.个人")
async def fps(
    app: Ariadne,
    group: Group,
    re: Match[bool],
    message: MessageChain,
    member: Member,
    id: Match[int],
    main_args: Match[str],
):
    if not id.available and main_args.available:
        return
    allowlist = kayaku.create(AllowList)
    if main_args.result not in allowlist.allow_private:
        await app.send_group_message(group, "哪来的功能，没这玩意")
        return
    if re.result:
        allowlist.allow_private[main_args.result].remove(id.result)
        await app.send_group_message(
            group,
            f"已撤销 {id.result} 的 {main_args.result} 访问权",
        )
        return
    allowlist.allow_private[main_args.result].append(id.result)
    await app.send_group_message(
        group,
        f"已授权 {id.result} 的 {main_args.result} 访问权",
    )


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("放行.群员")
async def fgm(
    app: Ariadne,
    group: Group,
    re: Match[bool],
    message: MessageChain,
    member: Member,
    gid: Match[int],
    id: Match[int],
    main_args: Match[str],
):
    if not id.available and main_args.available and gid.available:
        return
    allowlist = kayaku.create(AllowList)
    if main_args.result not in allowlist.allow_group_member:
        await app.send_group_message(group, "哪来的功能，没这玩意")
        return
    if re.result:
        allowlist.allow_group_member[main_args.result][str(gid.result)].remove(
            id.result
        )
        await app.send_group_message(
            group,
            f"已撤销 {gid.result} {id.result} 的 {main_args.result} 访问权",
        )
        return
    allowlist.allow_group_member[main_args.result][str(gid.result)].append(id.result)
    await app.send_group_message(
        group,
        f"已授权 {gid.result} {id.result} 的 {main_args.result} 访问权",
    )


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("ban.群组")
async def bgp(
    app: Ariadne,
    group: Group,
    re: Match[bool],
    message: MessageChain,
    member: Member,
    gid: Match[int],
    main_args: Match[str],
):
    if not gid.available and main_args.available:
        return
    banlist = kayaku.create(BanList)
    if main_args.result not in banlist.ban_group:
        await app.send_group_message(group, "哪来的功能，没这玩意")
        return
    if re.result:
        banlist.ban_group[main_args.result].remove(gid.result)
        await app.send_group_message(
            group,
            f"已 unban {gid.result} 的 {main_args.result}",
        )
        return
    banlist.ban_group[main_args.result].append(gid.result)
    await app.send_group_message(
        group,
        f"已 ban {gid.result}  的 {main_args.result}",
    )


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("ban.个人")
async def bps(
    app: Ariadne,
    group: Group,
    re: Match[bool],
    message: MessageChain,
    member: Member,
    id: Match[int],
    main_args: Match[str],
):
    if not id.available and main_args.available:
        return
    banlist = kayaku.create(BanList)
    if main_args.result not in banlist.ban_private:
        await app.send_group_message(group, "哪来的功能，没这玩意")
        return
    if re.result:
        banlist.ban_private[main_args.result].remove(id.result)
        await app.send_group_message(
            group,
            f"已 ban {id.result} 的 {main_args.result}",
        )
        return
    banlist.ban_private[main_args.result].append(id.result)
    await app.send_group_message(
        group,
        f"已撤销 {id.result} 的 {main_args.result} ban",
    )


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(MasterPermission()))
@assign("ban.群员")
async def bgm(
    app: Ariadne,
    group: Group,
    re: Match[bool],
    message: MessageChain,
    member: Member,
    gid: Match[int],
    id: Match[int],
    main_args: Match[str],
):
    if not id.available and main_args.available and gid.available:
        return
    banlist = kayaku.create(BanList)
    if main_args.result not in banlist.ban_group_member:
        await app.send_group_message(group, "哪来的功能，没这玩意")
        return
    if re.result:
        banlist.ban_group_member[main_args.result][str(gid.result)].remove(id.result)
        await app.send_group_message(
            group,
            f"已 ban {gid.result} {id.result} 的 {main_args.result}",
        )
        return
    banlist.ban_group_member[main_args.result][str(gid.result)].append(id.result)
    await app.send_group_message(
        group,
        f"已撤销 {gid.result} {id.result} 的 {main_args.result} ban",
    )
