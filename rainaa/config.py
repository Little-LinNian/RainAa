from dataclasses import field
from typing import List
from kayaku import config, initialize
from graia.saya import Channel

initialize({"rainaa_config.{**}": "./kayaku/kayaku.jsonc::{**}"})


@config("rainaa_config.mirai")
class MiraiConfig:
    account: int
    "Account: ep. 1145141145"
    verify_key: str
    "mah verify_key: ep. mymiraiapihttpverify_key"
    host: str
    "mah host: ep. http://11.45.1.4:8080"


@config("rainaa_config.saya")
class SayaConfig:
    module_path: str = "./module"
    'ep. "./module"'
    deprecated_prefix: str = "deprecated_"
    deprecated_modules: List[str] = field(default_factory=list)


@config("rainaa_config.bot")
class BotConfig:
    master: int
    admins: List[int]
    bot_name: str
    master_denied_message: List[str]


@config("rainaa_config.function_control")
class FunctionControl:
    functions: list[str] = field(default_factory=list)


@config("rainaa_config.banlist")
class BanList:
    ban_group: dict[str, list[int]] = field(default_factory=dict)
    ban_private: dict[str, list[int]] = field(default_factory=dict)
    ban_group_member: dict[str, dict[str, list[int]]] = field(default_factory=dict)


@config("rainaa_config.allowlist")
class AllowList:
    allow_group: dict[str, list[int]] = field(default_factory=dict)
    allow_private: dict[str, list[int]] = field(default_factory=dict)
    allow_group_member: dict[str, dict[str, list[int]]] = field(default_factory=dict)
