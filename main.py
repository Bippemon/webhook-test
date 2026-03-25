from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from os.path import exists
from zoneinfo import ZoneInfo

import json
import os

os.makedirs("logs", exist_ok=True)
LOG_PATH = "logs/logs.csv"

if exists(LOG_PATH):
    pass
else:
    with open(mode='x', file=LOG_PATH) as f:
        f.write("time,device_name,temperature,humidity,dr,fcnt,milesight_rssi,milesight_snr,dragino_rssi,dragino_snr\n")


class SensorData(BaseModel):
    deduplicationId: str
    time: str
    deviceInfo: dict # JSON
    devAddr: str
    adr: bool
    dr: int
    fCnt: int
    fPort: int
    confirmed: bool
    data: str
    object: dict # JSON
    rxInfo: list
    txInfo: dict # JSON

app = FastAPI()

@app.post("/uplink")
async def create_sensor_data_obj(data: SensorData):
    time = sweden_time(data.time)
    
    device_name = data.deviceInfo["deviceName"]
    temperature = data.object.get("temperature")
    humidity = data.object.get("humidity")

    milesight_gw = os.getenv("MILESIGHT_GW")
    dragino_gw = os.getenv("DRAGINO_GW")

    milesight_rssi = None
    milesight_snr = None
    dragino_rssi = None
    dragino_snr = None

    for i in data.rxInfo:
        if i["gatewayId"] == milesight_gw:
            milesight_rssi = i["rssi"]
            milesight_snr = i["snr"]

        if i["gatewayId"] == dragino_gw:
            dragino_rssi = i["rssi"]
            dragino_snr = i["snr"]

    if temperature is None and humidity is None:
        return 201

    write_data(time, device_name, temperature, humidity, data.dr, data.fCnt, milesight_rssi, milesight_snr, dragino_rssi, dragino_snr)
    return 200


def write_data(time, device_name, temperature, humidity, dr, fcounter, milesight_rssi, milesight_snr, dragino_rssi, dragino_snr):
    with open(mode="a", file=LOG_PATH) as f:
        f.write(f"{time},{device_name},{temperature},{humidity},{dr},{fcounter},{milesight_rssi},{milesight_snr},{dragino_rssi},{dragino_snr}\n")


def sweden_time(time):
    time_short = datetime.fromisoformat(time)
    time_sweden = time_short.astimezone(ZoneInfo("Europe/Stockholm"))
    time_sweden = time_sweden.strftime("%Y-%m-%d %H:%M:%S")

    return time_sweden


if __name__ == "__main__":
    with open("example_json_obj/cs_uplink.json") as f:
        obj = f.read()
        json_obj = json.loads(obj)

    obj_time = json_obj["time"]
    
    # account for data sent as UTC (+00:00)
    # time = datetime.now(timezone.utc).isoformat()
    # print(f"time now: {time}")

    time_sweden = sweden_time(obj_time)
    print(time_sweden)