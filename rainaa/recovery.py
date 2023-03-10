import os
from pathlib import Path
from zipfile import ZipFile

import requests
from loguru import logger
from tqdm import tqdm


def download(url: str, fname: str):
    # 用流stream的方式获取url的数据
    resp = requests.get(url, stream=True)
    # 拿到文件的长度，并把total初始化为0
    total = int(resp.headers.get("content-length", 0))
    # 打开当前目录的fname文件(名字你来传入)
    # 初始化tqdm，传入总数，文件名等数据，接着就是写入，更新等操作了
    with open(fname, "wb") as file, tqdm(
        desc=fname,
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


class NotAFileError(Exception):
    pass


class Recovery:
    def sideload(self, ota_path: str):
        zippath = Path(ota_path)
        if not zippath.exists():
            raise FileNotFoundError(f"File not found: {zippath}")
        if not zippath.is_file():
            raise NotAFileError(f"Not a File: {zippath}")
        if not zippath.name.endswith(".zip"):
            raise NotAFileError(f"Not a zip file: {zippath}")
        with ZipFile(zippath, "r") as zip:
            zip.extractall("./ota_cache/")
        deep = "./ota_cache/"
        path_deep = Path(deep)
        flashed = []
        for root, dirs, files in os.walk(deep, topdown=False):

            for name in files:
                if name == "update.zip":
                    continue
                path = Path(root) / name
                path = str(path)
                flashed.append(self.flash(path, path.replace(str(path_deep), "./")))
        return flashed

    def esideload(self, ota_url: str):
        logger.info(f"Downloading OTA from {ota_url}")
        for i in range(3):
            try:
                Path("./ota_cache").mkdir(parents=True, exist_ok=True)
                download(ota_url, "./ota_cache/update.zip")
                break
            except Exception as e:
                logger.exception(e)
                logger.warning(f"Download failed, retrying... ({i+1}/3)")
            finally:
                if i == 2:
                    logger.error("Download failed, aborting...")
                    return False
        return self.sideload("./ota_cache/update.zip")

    def cleanup(self):
        os.rmdir("./ota_cache")
        os.rmdir("./ota_backup")

    @staticmethod
    def touch_with_mkdir(path: str):
        parent = Path(path).parent
        parent.mkdir(parents=True, exist_ok=True)
        Path(path).touch()

    @staticmethod
    def flash(src: str, dest: str):
        logger.info(f"Flashing {src} to {dest}")
        Path("./ota_backup").mkdir(parents=True, exist_ok=True)
        if Path(src).exists() and Path(dest).exists():
            if not Path(f"./ota_backup/{src}").exists():
                Recovery.touch_with_mkdir(f"./ota_backup/{dest}")
            os.replace(dest, f"./ota_backup/{dest}")
        if not Path(src).exists():
            Recovery.touch_with_mkdir(src)
            os.replace(dest, src)
        if not Path(dest).exists():
            Recovery.touch_with_mkdir(dest)
            os.replace(src, dest)
        return f"Falshed {src} to {dest}"


recovery = Recovery()


def blocking():
    logger.info("Recovery mode")
    while True:
        ...
