import json
import os
import time

from rainaa.rdb import rdb

if __name__ == "__main__":
    rdb.boot("system")
    scan_time = 0
    last_data = {}
    while True:
        with open("rdb_interface.json", "r") as f:
            if not f.read():
                scan_time += 1
                time.sleep(1)
                continue
            f.seek(0)
            data = json.load(f)
            with open("rdb_interface.json", "w") as f:
                ...
        if data == last_data:
            scan_time += 1
            time.sleep(1)
            continue
        if data["command"] == "ota":
            msg = rdb.ota(data["url"])
            source = data["source"]
            rdb.reboot("system")
            with open("rdb_message.json", "w") as f:
                json.dump(
                    {
                        "message": msg,
                        "source": source,
                    },
                    f,
                )
        elif data["command"] == "sideload":
            rdb.sideload(data["path"])
            rdb.reboot("system")
        elif data["command"] == "reboot":
            rdb.reboot(data["partition"])
        elif data["command"] == "shutdown":
            rdb.shutdown()
            break
        scan_time += 1
        time.sleep(1)
