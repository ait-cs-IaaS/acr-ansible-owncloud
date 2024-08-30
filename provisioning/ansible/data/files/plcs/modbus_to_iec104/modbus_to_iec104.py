# docker run -t -e SHIFT_OPENPLC_IP=10.5.0.4 --rm --ip 10.5.0.10 --network=shift_network -p 2405:2405 -t modbus_to_iec104 modbus_to_iec104

import logging
import os
import threading
import time

from pymodbus.client import ModbusTcpClient
import c104
from pymodbus.exceptions import ModbusException

from point import point_factory, Point, ReadPoint, CommandPoint

lock = threading.Lock()
points = point_factory()
read_values = {}
command_values = {}
modbus_read_error = True

loglevel = logging.DEBUG if os.getenv("SHIFT_DEBUG") in ["false", "False", "FALSE", "0", 0] else logging.WARNING

logging.basicConfig(filename="modbus_to_iec104.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=loglevel)

logger = logging.getLogger(__name__)

class C104PointCallbacks:
        def __init__(self, point: Point):
                # This is a trick to provide context to the callable, passed as argument to c104.Point.on_before_read()
                #  only working with the below set signature.
                self._point = point

        def on_before_read_callback(self, point: c104.Point) -> None:
                global read_values

                with lock:
                        point.value = read_values[self._point.name]
                        print(f"READ {self._point.name}: {read_values[self._point.name]}")

        def on_receive_callback(self, point: c104.Point, previous_state: dict, message: c104.IncomingMessage) -> c104.ResponseState:
                global command_values

                with lock:
                        command_values[self._point.name] = message.value

                return c104.ResponseState.SUCCESS  # TODO implement


def modbus_client():
        # TODO handle termination explicitly

        global lock, modbus_read_error, points, read_values, command_values

        modbus_server_ip = os.getenv("SHIFT_OPENPLC_IP")
        if not modbus_server_ip:
                logger.error("SHIFT_OPENPLC_IP environment variable not set")
                os._exit(1)

        client = ModbusTcpClient(modbus_server_ip, timeout=1) # TODO turn into env var

        # TODO implement: reconnect if disconnected for a while
        while True:
                _modbus_read_error = False
                if not client.connected:
                        _modbus_read_error = True
                        if client.connect():
                                print(f"Connection to Modbus server established. Socket {client.socket.getsockname()}")
                        else:
                                print(f"Connection to Modbus server ({client.comm_params.host}, {client.comm_params.port}) failed")

                print(f"=== NEW FRAME: {time.time()} ===")
                _read_values = {}

                for point in points.values():
                        if type(point) is ReadPoint:
                                try:
                                        modbus_read = getattr(client, point.pymodbus_read_method)
                                        _read_values[point.name] = modbus_read(point.plc_address)
                                        _read_values[point.name] = getattr(_read_values[point.name], point.pymodbus_value_property)[0]

                                except (ModbusException, AttributeError) as e:
                                        logger.warning(f"Modbus to IEC104 [Reading] {point.name} {point.plc_address_string} - {e}")
                                        _read_values[point.name] = point.default_value
                                        _modbus_read_error = True

                        elif type(point) is CommandPoint:
                                with lock:
                                        _command_value = command_values.get(point.name, None)

                                if _command_value is None:
                                        continue

                                _command_value = point.convert_value_iec104_to_modbus(_command_value)
                                try:
                                        modbus_write = getattr(client, point.pymodbus_command_method)

                                        _status = modbus_write(point.plc_address, _command_value)
                                        if _status.isError():
                                                raise ModbusException(str(_status))
                                        else:
                                                print(f"COMMAND {point.name}: {_command_value}")
                                                command_values[point.name] = None

                                except (ModbusException, AttributeError) as e:
                                        logger.warning(
                                                f"Modbus to IEC104 [Command] {point.name} {point.plc_address_string} - {e}")

                with lock:
                    read_values = _read_values
                    modbus_read_error = _modbus_read_error

                # modbus query interval
                time.sleep(1) # TODO make configurable

def iec104_server():
        def _c104_point_modbus_read_error_callback(point: c104.Point) -> None:
                global modbus_read_error
                with lock:
                        point.value = modbus_read_error

        global points

        port = os.getenv("SHIFT_IEC104_SERVER_PORT", 2405)
        port = int(port)

        server = c104.Server(ip="0.0.0.0", port=port)
        station = server.add_station(common_address=47)

        c104_points = {}
        for point in points.values():
                c104_points[point.name] = station.add_point(io_address=point.iec104_address, type=point.c104_point_type)

                if type(point) is ReadPoint:
                        c104_points[point.name].on_before_read(callable=C104PointCallbacks(point).on_before_read_callback)
                elif type(point) is CommandPoint:
                        c104_points[point.name].on_receive(callable=C104PointCallbacks(point).on_receive_callback)

        c104_points["modbus_read_error"] = station.add_point(io_address=10, type=c104.Type.M_SP_NA_1)
        c104_points["modbus_read_error"].on_before_read(callable=_c104_point_modbus_read_error_callback)

        server.start()

        while True:
                time.sleep(1) # TODO make configurable

if __name__ == "__main__":
        
        modbus_thread = threading.Thread(target=modbus_client, daemon=True)
        modbus_thread.start()

        # c104.set_debug_mode(c104.Debug.Server)
        iec104_server()
