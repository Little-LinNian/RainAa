from launart import Launart
from loguru import logger
from rainaa.services import ConfigService
from rainaa.config import MiraiConfig
from rainaa.tools.alc_sender import (
    alconna_help_sender,
)
from rainaa.all import install
from creart import create
from graia.ariadne.app import Ariadne
from arclet.alconna.manager import (
    command_manager,
)
from arclet.alconna.graia import (
    AlconnaDispatcher,
    AlconnaBehaviour,
)
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.broadcast import Broadcast
from graia.saya import Saya
import kayaku

bcc = create(Broadcast)
saya = create(Saya)
saya.install_behaviours(AlconnaBehaviour(bcc, command_manager))
launart = Launart()
launart.add_service(ConfigService())
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
app = Ariadne(
    connection=config(
        mirai_config.account,
        mirai_config.verify_key,
        HttpClientConfig(host=mirai_config.host),
        WebsocketClientConfig(host=mirai_config.host),
    ),
)
app.launch_blocking()
