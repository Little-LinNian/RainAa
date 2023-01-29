from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graiax.shortcut.saya import listen
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graiax.fastapi import RouteSchema
import jionlp
from fastapi.responses import Response
from loguru import logger
import time
from pathlib import Path
import random
import hashlib

channel = Channel.current()



# Gocq api 仿制,实现 pushoo 博客评论推送
# Key 为 机器人的 qq 号 + 启动时间 + 一个随机数 的 md5 值
randint = random.randint(0,100000)
startup_time = int(time.time())

def gen_key(qq: int, time: int, random: int):
    with open("key.txt","w",encoding="utf-8") as f:
        key = hashlib.md5(f"{qq}{time}{random}".encode("utf-8")).hexdigest()
        f.write(key)

def key_now():
    with open("key.txt","r",encoding="utf-8") as f:
        key = f.read()
        return key

@listen(ApplicationLaunched)
async def gtoken(app: Ariadne):
    if not Path("key.txt").exists():
        gen_key(app.account,startup_time,randint)
    key = key_now()
    logger.info(f"FakeGocQ api 已启动，key 为 {key}")
    time.sleep(5)
    

@channel.use(RouteSchema("/send_private_msg", methods=["GET"]))
async def spm(message: str, user_id: int, token: str):
    app = Ariadne.current()
    message = jionlp.remove_ip_address(message) # 移除 ip 地址
    if token == key_now(app.account,startup_time,randint):
            message_id = await app.send_friend_message(user_id, message)
            return {"status": "ok", "data": {"message_id": message_id}}
    else:
        return Response(status_code=403,content="403 Forbidden")

    

@channel.use(RouteSchema("/send_group_msg", methods=["GET"]))
async def sgm(message: str, group_id: int, token: str):
    app = Ariadne.current()
    message = jionlp.remove_ip_address(message) # 移除 ip 地址
    if token == key_now(app.account,startup_time,randint):
            message_id = await app.send_group_message(group_id, message)
            return {"status": "ok", "data": {"message_id": message_id}}
    else:
        return Response(status_code=403,content="403 Forbidden")
