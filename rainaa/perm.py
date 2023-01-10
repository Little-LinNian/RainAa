import abc
import random
from multiprocessing import Event
from types import TracebackType
from typing import List, Optional, Union

from graia.ariadne import Ariadne
from graia.ariadne.event.message import (GroupMessage, MessageEvent,
                                         OtherClientMessage)
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

import kayaku
from rainaa.config import AllowList, BanList, BotConfig, FunctionControl


class BasePermission:

    denied_message: Optional[List[str]] = None

    def __init__(
        self,
        denied_message: Optional[List[str]] = None,
    ):
        self.denied_message = denied_message

    @abc.abstractmethod
    async def target(self, event: BaseEvent) -> bool:
        raise NotImplementedError()


class PermissionStatus:
    def __init__(self, status: bool):
        self.status = status


class PersonPermission(BasePermission):
    def __init__(
        self,
        sender: int,
        denied_message: Optional[List[str]] = None,
    ):
        self.denied_message = denied_message
        self.sender = sender

    async def target(self, event: MessageEvent) -> bool:
        return event.sender.id == self.sender


class Ban(BasePermission):
    def __init__(
        self,
        func_name: str,
        denied_message: Optional[List[str]] = None,
    ):
        kayaku.create(FunctionControl).functions.append(func_name)
        self.denied_message = denied_message
        self.func_name = func_name

    async def target(self, event: MessageEvent) -> bool:
        banlist = kayaku.create(BanList)
        if not self.func_name in banlist.ban_private:
            banlist.ban_private[self.func_name] = []
        if isinstance(event, GroupMessage):
            if not self.func_name in banlist.ban_group:
                banlist.ban_group[self.func_name] = []
            if not self.func_name in banlist.ban_group_member:
                banlist.ban_group_member[self.func_name] = {}
            if (
                str(event.sender.group.id) in banlist.ban_group_member[self.func_name]
                and event.sender.id
                in banlist.ban_group_member[self.func_name][str(event.sender.group.id)]
            ):
                return False
            elif event.sender.group.id in banlist.ban_group[self.func_name]:
                return False
        return (
            isinstance(event, OtherClientMessage)
            or event.sender.id not in banlist.ban_private
        )


class Allow(BasePermission):
    def __init__(
        self,
        func_name: str,
        denied_message: Optional[List[str]] = None,
    ):
        self.denied_message = denied_message
        self.func_name = func_name
        kayaku.create(FunctionControl).functions.append(self.func_name)

    async def target(self, event: MessageEvent) -> bool:
        allowlist = kayaku.create(AllowList)
        if not self.func_name in allowlist.allow_private:
            allowlist.allow_private[self.func_name] = []
        if isinstance(event, GroupMessage):
            if not self.func_name in allowlist.allow_group:
                allowlist.allow_group[self.func_name] = []
            if not self.func_name in allowlist.allow_group_member:
                allowlist.allow_group_member[self.func_name] = {}

            if (
                str(event.sender.group.id)
                in allowlist.allow_group_member[self.func_name]
                and event.sender.id
                in allowlist.allow_group_member[self.func_name][
                    str(event.sender.group.id)
                ]
            ):
                return True
            elif event.sender.group.id in allowlist.allow_group[self.func_name]:
                return True

        return (
            not isinstance(event, OtherClientMessage)
            and event.sender.id in allowlist.allow_private
        )


class MasterPermission(PersonPermission):
    def __init__(self):
        cfg = kayaku.create(BotConfig)
        self.denied_message = cfg.master_denied_message
        self.sender = cfg.master


class AdminPermission(PersonPermission):
    def __init__(
        self,
        denied_message: Optional[List[str]] = None,
    ):
        self.denied_message = denied_message

    def target(self, event: MessageEvent) -> bool:
        cfg = kayaku.create(BotConfig)
        return event.sender.id in cfg.admins


class Stop(BasePermission):
    async def target(self, event: BaseEvent) -> bool:
        return False


class AllAllow(BasePermission):
    def __init__(self):
        pass

    async def target(self, event: BaseEvent) -> bool:
        return True


class PermissionDispatcher(BaseDispatcher):
    def __init__(
        self,
        permission: BasePermission,
    ):
        """
        :param permission: 权限
        """
        self.permission = permission

    async def afterDispatch(
        self,
        interface: DispatcherInterface,
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        denied_message = self.permission.denied_message
        if await self.permission.target(interface.event):
            return interface
        if denied_message:
            denied_message = random.choice(denied_message)
            if not isinstance(denied_message, MessageChain):
                denied_message = MessageChain(denied_message)
            app = Ariadne.current()
            await app.send_message(
                interface.event,
                denied_message,
            )
        raise ExecutionStop()

    async def catch(self, interface: DispatcherInterface):
        return await super().catch(interface)
