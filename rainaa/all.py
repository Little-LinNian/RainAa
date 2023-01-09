from typing import List
from loguru import logger
from .config import (
    SayaConfig,
    FunctionControl,
)
import os
from pathlib import Path
from time import sleep
from graia.saya import Saya
import kayaku


def install(saya: Saya):
    saya_cfg = kayaku.create(SayaConfig)
    functions = kayaku.create(FunctionControl)
    functions.functions = []
    deprecated: List[str] = []
    with saya.module_context():
        saya_cfg.deprecated_modules = []
        for i in os.listdir(saya_cfg.module_path):
            try:
                if i.startswith(saya_cfg.deprecated_prefix):
                    logger.info(f"忽略模块 {i}")
                    saya.require(i)
                    deprecated.append(i)
                    continue
                if i.startswith("__"):
                    continue
                if i.endswith(".py"):
                    i = i.removesuffix(".py")
                    saya.require(f"{saya_cfg.module_path}.{i}")
                    logger.info(f"Loaded module {i}")
                elif Path(f"./modules_modified/{i}").is_dir():
                    saya.require(f"modules_modified.{i}")
                    logger.info(f"Loaded module {i}")
            except Exception as e:
                logger.exception(e)
            sleep(0.3)
    for i in deprecated:
        m = saya.channels.get(i)
        if not m:
            continue
        saya_cfg.deprecated_modules.append(i)
        saya.uninstall_channel(m)
