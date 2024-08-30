# docker run -t -e SHIFT_MODBUS_TO_IEC104_IP=10.5.0.10 --rm --ip 10.5.0.11 --network=shift_network -p 8888:8888 --name iec104_to_http iec104_to_http
# run: uvicorn iec104_2_rest_api:app --port 8888

import logging
import os
import threading
import time
from pydantic import BaseModel, Field

import c104

from point import point_factory, ReadPoint, CommandPoint, Point

loglevel = logging.DEBUG if os.getenv("SHIFT_DEBUG") in ["false", "False", "FALSE", "0", 0] else logging.WARNING

logging.basicConfig(filename="hmi.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=loglevel)

logger = logging.getLogger(__name__)

def on_receive_raw_callback(connection: c104.Connection, data: bytes) -> None:
    global raw_values
    columns = [column.strip() for column in c104.explain_bytes(apdu=data).split("|")] + [data.hex()]
    raw_values.append(columns)

def iec104_client():
    # c104.set_debug_mode(c104.Debug.Client|c104.Debug.Connection)

    iec104_server_ip = os.getenv("SHIFT_MODBUS_TO_IEC104_IP")
    if not iec104_server_ip:
        logger.error("SHIFT_OPENPLC_IP environment variable not set")
        os._exit(1)

    port = os.getenv("SHIFT_MODBUS_TO_IEC104_PORT", 2405)
    port = int(port)

    client = c104.Client(tick_rate_ms=1000, command_timeout_ms=100) # TODO adjust timeout, make configurable
    connection = client.add_connection(ip=iec104_server_ip, port=port, init=c104.Init.INTERROGATION)
    connection.on_receive_raw(callable=on_receive_raw_callback)
    station = connection.add_station(common_address=47)

    c104_points = {}
    for _point in points.values():
        c104_points[_point] = station.add_point(io_address=_point.iec104_address, type=_point.c104_point_type)

    client.start()

    while not connection.is_connected:
        print("Waiting for connection to {0}:{1}".format(connection.ip, connection.port))
        time.sleep(1)

    global command_values, iec104_read_values, raw_values

    while True:
        with lock:
            raw_values = []

        _read_values = {}
        _read_values[iec104_read_error_point] = 0

        print(f"=== NEW FRAME: {time.time()} ===")
        for _point, c104_point in c104_points.items():
            if type(_point) is ReadPoint:
                # TODO understand why this returning false negatives sometimes. Perhaps replace this by getting value from
                #   Point.on_receive(IncomingMessage.value)
                if c104_point.read(): # TODO else log warning
                    # turn int16 to uint16
                    _value = int(c104_point.value)
                    _value = _value if _value >= 0 else _value + (2 ** 16)

                    print(f"READ {_point.name} {_value}")
                    _read_values[_point] = _value
                else:
                    _read_values[iec104_read_error_point] = 1


            elif type(_point) is CommandPoint:
                with lock:
                    _command_value = command_values.get(_point.name, None)

                    if _command_value is None:
                        continue

                    c104_point.value = _command_value
                    _success = c104_point.transmit(cause=c104.Cot.ACTIVATION)

                    if _success:
                        print(f"COMMAND IEC104: {_point.name}: {c104_point.value}")
                        command_values[_point.name] = None

                    else:
                        print(f"ERROR COMMAND IEC104 {_point.name}: {c104_point.value} unsuccessful")


        with lock:
            iec104_read_values = _read_values

        time.sleep(1)


lock = threading.Lock()

points = point_factory()
points["modbus_read_error"] = ReadPoint(iec104_address=10, name="modbus_read_error", plc_address="QX99.9")  # dummy plc_address
iec104_read_error_point = ReadPoint(iec104_address=9, name="iec104_read_error", plc_address="QX99.9")  # dummy plc_address

# default values
raw_values = []
command_values = {}
iec104_read_values = {iec104_read_error_point: 1}

iec104_thread = threading.Thread(target=iec104_client, daemon=True)
iec104_thread.start()

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, use specific domains for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

with open(os.path.dirname(__file__) + "/hmi.html") as fh:
    html = fh.read()

with open(os.path.dirname(__file__) + "/hmi.svg") as fh:
    svg = fh.read()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTMLResponse(content=html)

@app.get("/hmi.svg", response_class=HTMLResponse)
def read_svg():
    return HTMLResponse(content=svg)

@app.get("/sprite.png", response_class=FileResponse)
def read_sprite():
    return FileResponse(path=os.path.dirname(__file__) + "/img/indicator_sprite.png")

@app.post("/shutdown")
def post_shutdown():
    global command_values
    with lock:
        command_values["shutdown_command"] = points["shutdown_command"].message_encode(1)
    return {"success": True}

class TargetPower(BaseModel):
    # TODO define max valid value based on max modbus value minus max noise based on common source of truth
    target_power_command: int = Field(1_000_000, ge=1, le=9_000_000)

@app.post("/target_power")
def post_target_power(data: TargetPower):
    global command_values, points
    with lock:

        print(f"COMMAND HTTP: target_power_command: {data.target_power_command}")
        try:
            command_values["target_power_command"] = points["target_power_command"].message_encode(data.target_power_command)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=e)

    return {"success": True}

def pad_raw_values(rows: list) -> list:
    new_rows = []
    for row in rows:
        if len(row) > 8:
            print("WARNING raw values more than 8. It was assumed this is not possible, html debug table needs adjusting.")
            print (row)

        # Pad raw_values list to 8 elements, with the raw value always being the last.
        firsts = row[:-1]
        last = row[-1]

        new_rows.append(firsts + [""] * (7 - len(firsts)) + [last])
    return new_rows

@app.get("/iec104")
def read_item():
    global iec104_read_values, raw_values

    http_read_values = {
        "human": {},
        "raw": []
    }

    for point, iec104_value in iec104_read_values.items():
        http_read_values["human"][point.name] = point.message_decode(iec104_value)

    raw_values = pad_raw_values(raw_values)

    http_read_values["raw"] = raw_values

    with lock:
        return http_read_values
