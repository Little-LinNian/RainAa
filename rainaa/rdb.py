import multiprocessing
import os

from loguru import logger

from rainaa.recovery import recovery


def _boot_pool(partition: str):
    if partition == "recovery":
        from rainaa.recovery import blocking

        blocking()
    elif partition == "system":
        from main import app

        app.launch_blocking()


class RainAaDeveloperBridge:
    def __init__(self):
        ...

    def boot(self, partition: str):
        if partition == "recovery":
            p = multiprocessing.Process(target=_boot_pool, args=("recovery",))
        elif partition == "system":
            p = multiprocessing.Process(target=_boot_pool, args=("system",))
        else:
            raise ValueError("Invalid partition")
        self.is_running = partition
        self._process = p
        self._process.start()

    def shutdown(self):
        if isinstance(self._process.pid, int):
            os.kill(self._process.pid, 9)
        self.is_running = ""

    def reboot(self, partition: str):
        if self.is_running:
            self.shutdown()
        self.boot(partition)

    def sideload(self, path: str):
        if not self.is_running == "recovery":
            logger.error("Not in recovery")
            self.shutdown()
            return
        logger.info(f"Sideload {path}")
        recovery.sideload(path)

    def ota(self, url: str):
        if not self.is_running == "recovery":
            logger.info("Rebooting to recovery")
            self.reboot("recovery")
        logger.info(f"OTA {url}")
        resp = recovery.esideload(url)
        if not resp:
            logger.error("OTA failed")
            self.shutdown()
            return
        logger.info("OTA success")
        return "OTA success\n" + "\n".join(resp)


rdb = RainAaDeveloperBridge()
