from .text2image import text2image
from graia.ariadne.message.chain import (
    MessageChain,
)
from graia.ariadne.message.element import (
    Image,
)


async def alconna_help_sender(output: str):
    return MessageChain(Image(data_bytes=await text2image(output)))
