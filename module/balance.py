from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import (
    MessageChain,
)
from graia.ariadne.message.element import (
    Source,
)
from graia.ariadne.util.cooldown import (
    CoolDown,
)
from graia.ariadne.model import Group, Member
from graiax.shortcut.saya import dispatch
from bce.public.api import (
    balance_chemical_equation,
)
from bce.option import Option
from rainaa.perm import (
    Ban,
    PermissionDispatcher,
)
from arclet.alconna.graia import (
    alcommand,
    Match,
)
from arclet.alconna import (
    Alconna,
    Args,
    CommandMeta,
)

alc = Alconna(
    "!配平",
    Args["main_args", str],
    meta=CommandMeta(
        "配平化学方程式",
        example="!配平 C6H12O6+O2=CO2+H2O",
        fuzzy_match=True,
    ),
)


@alcommand(alc, send_error=True)
@dispatch(CoolDown(1.5))
@dispatch(PermissionDispatcher(Ban("balance", ["本群还没开放"])))
async def setu(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    member: Member,
    source: Source,
    main_args: Match[str],
):
    exp = main_args.result
    try:
        resp = balance_chemical_equation(exp, Option())
        if isinstance(resp, str):
            await app.send_group_message(
                group,
                f"配平完成\n{resp}",
                quote=source,
            )
    except Exception as e:
        await app.send_group_message(
            group,
            f"配平失败\n{str(e)}",
            quote=source,
        )
