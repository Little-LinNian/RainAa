from arclet.alconna.graia import AlconnaBehaviour, AlconnaDispatcher
from arclet.alconna.manager import command_manager
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (HttpClientConfig,
                                             WebsocketClientConfig, config)
from graia.amnesia.builtins.uvicorn import UvicornService
from graiax.fastapi.service import FastAPIService
from graiax.fastapi.saya.behaviour import FastAPIBehaviour
from graia.broadcast import Broadcast
from graia.saya import Saya
from launart import Launart
from loguru import logger
from fastapi import FastAPI

import kayaku
from rainaa.all import install
from rainaa.config import MiraiConfig, FakeGoCQConfig
from rainaa.services import ConfigService
from rainaa.tools.alc_sender import alconna_help_sender

bcc = create(Broadcast)
saya = create(Saya)
fastapi = FastAPI()
saya.install_behaviours(AlconnaBehaviour(bcc, command_manager))
saya.install_behaviours(FastAPIBehaviour(fastapi))
launart = Launart()
launart.add_service(ConfigService())
launart.add_service(FastAPIService(fastapi))
AlconnaDispatcher.default_send_handler = alconna_help_sender
try:
    kayaku.bootstrap()
except Exception as e:
    logger.exception(e)
    kayaku.save_all()
    logger.warning("配置文件未按要求填写完成，请自行编辑 ./kayaku/main.jsonc")
    quit()
install(saya)
Ariadne.config(launch_manager=launart)
mirai_config = kayaku.create(MiraiConfig)
fakegocq = kayaku.create(FakeGoCQConfig)
launart.add_service(UvicornService(host=fakegocq.sever, port=fakegocq.port))
app = Ariadne(
    connection=config(
        mirai_config.account,
        mirai_config.verify_key,
        HttpClientConfig(host=mirai_config.host),
        WebsocketClientConfig(host=mirai_config.host),
    ),
)
if __name__ == "__main__":
    app.launch_blocking()
