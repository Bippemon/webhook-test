from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from os.path import exists
import json

LOG_PATH = "logs/logs.csv"

if exists(LOG_PATH):
    pass
else:
    with open(mode='x', file=LOG_PATH) as f:
        f.write("time, device_name, temperature, humidity\n")


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
    time_short = datetime.fromisoformat(data.time).strftime("%Y-%m-%d %H:%M:%S")
    device_name = data.deviceInfo["deviceName"]
    temperature = data.object["temperature"]
    humidity = data.object.get("humidity")

    # print("Time       :", time_short)
    # print("Device name:", data.deviceInfo["deviceName"])
    # print("Temperature:", data.object["temperature"])
    # print(f"Humidity    {data.object.get('humidity')}%")
    
    write_data(time_short, device_name, temperature, humidity)
    return data


def write_data(time, device_name, temperature, humidity):
    with open(mode="a", file=LOG_PATH) as f:
        f.write(f"{time}, {device_name}, {temperature}, {humidity}\n")