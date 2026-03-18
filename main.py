from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from os.path import exists
import os

LOG_PATH = "logs/logs.csv"

if exists(LOG_PATH):
    pass
else:
    with open(mode='x', file=LOG_PATH) as f:
        f.write("time, device_name, temperature, humidity, dr, milesight_rssi, milesight_snr, dragino_rssi, dragino_snr\n")


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
    rxInfo: list # JSON
    txInfo: dict # JSON


app = FastAPI()

@app.post("/uplink")
async def create_sensor_data_obj(data: SensorData):
    # account for data sent as UTC (+00:00)
    time_short = datetime.fromisoformat(data.time) + timedelta(hours=1)
    time_short = time_short.strftime("%Y-%m-%d %H:%M:%S")
    
    device_name = data.deviceInfo["deviceName"]
    temperature = data.object["temperature"]
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
        return data

    write_data(time_short, device_name, temperature, humidity, data.dr, milesight_rssi, milesight_snr, dragino_rssi, dragino_snr)
    return data


def write_data(time, device_name, temperature, humidity, dr, milesight_rssi, milesight_snr, dragino_rssi, dragino_snr):
    with open(mode="a", file=LOG_PATH) as f:
        f.write(f"{time}, {device_name}, {temperature}, {humidity}, {dr}, {milesight_rssi}, {milesight_snr}, {dragino_rssi}, {dragino_snr}\n")