from launart import Launart, Launchable
import kayaku, asyncio

from loguru import logger


class ConfigService(Launchable):
    id = "bot.config"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {
            "preparing",
            "cleanup",
            "blocking",
        }

    async def launch(self, _mgr: Launart):
        async with self.stage("preparing"):
            # 在 preparing 阶段预加载模型并写入 JSON Schema
            kayaku.bootstrap()

        async with self.stage("cleanup"):
            # 在 cleanup 阶段写入所有模型
            kayaku.save_all()
