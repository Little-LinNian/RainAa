from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel

from kayaku import config, initialize

initialize({"main_config.{**}": "./kayaku/main.jsonc::{**}"})
initialize({"function_config.{**}": "./kayaku/function.jsonc::{**}"})
initialize({"chat_record_config.{**}": "./kayaku/chat_record.jsonc::{**}"})


@config("main_config.mirai")
class MiraiConfig:
    account: int
    "Account: ep. 1145141145"
    verify_key: str
    "mah verify_key: ep. mymiraiapihttpverify_key"
    host: str
    "mah host: ep. http://11.45.1.4:8080"


@config("main_config.saya")
class SayaConfig:
    module_path: str = "module"
    'ep. "module" dont include any "/" or "\\" use "." instead'
    deprecated_prefix: str = "deprecated_"
    'ep. "deprecated_114514.py"'
    deprecated_modules: List[str] = field(default_factory=list)
    "auto generated"


@config("main_config.bot")
class BotConfig:
    master: int
    admins: List[int]
    bot_name: str
    master_denied_message: List[str]


@config("function_config.function_control")
class FunctionControl:
    functions: list[str] = field(default_factory=list)


@config("function_config.banlist")
class BanList:
    ban_group: dict[str, list[int]] = field(default_factory=dict)
    ban_private: dict[str, list[int]] = field(default_factory=dict)
    ban_group_member: dict[str, dict[str, list[int]]] = field(default_factory=dict)


@config("function_config.allowlist")
class AllowList:
    allow_group: dict[str, list[int]] = field(default_factory=dict)
    allow_private: dict[str, list[int]] = field(default_factory=dict)
    allow_group_member: dict[str, dict[str, list[int]]] = field(default_factory=dict)
