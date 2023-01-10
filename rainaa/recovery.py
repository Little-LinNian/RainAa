import os
from pathlib import Path
from zipfile import ZipFile

import requests
from loguru import logger


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
                ota_file = requests.get(ota_url)
                Path("./ota_cache").mkdir(parents=True, exist_ok=True)
                with open("./ota_cache/update.zip", "wb") as f:
                    f.write(ota_file.content)
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
