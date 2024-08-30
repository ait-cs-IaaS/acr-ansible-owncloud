from abc import ABC
import csv
import os
import re
from typing import Dict

try:
    import c104
except ImportError:

    # in PSM we can't import c104, but we also don't need the functionality here, so we just mock it.
    class MockC104:
        class MockType:
            def __getattr__(self, item):
                return None  # doesn't matter
        Type = MockType()

    c104 = MockC104()


class Point(ABC):
    # We define our modbus value upper boundary at 2^15 instead of 2^16 so binary sequence would be interpreted the same
    # whether interpreted as int16 or uint16.
    ANALOG_MESSAGE_SIZE = pow(2, 15)
    BINARY_MESSAGE_SIZE = 1

    """
    Based on
    - https://openplcproject.com/docs/2-5-modbus-addressing/
    - https://spinengenharia.com.br/wp-content/uploads/2019/01/Protocol_IEC-60870-5-104_Slave.pdf
    - https://support.kaspersky.com/kicsfornetworks/4.1/en-US/206199.htm
    """

    def __init__(self, iec104_address: int, name: str, plc_address: str, max_value: int = -1):
        """
        :param iec104_address:
        :param name:
        :param plc_address:
        :param max_value: The maximum (not encoded) value the point make take. This value will be scaled up/down to fill
            the MESSAGE_SIZE of the point. If you want on scaling up/down, let max_value = MESSAGE_SIZE
            - -1 means default value
        """
        self.iec104_address = int(iec104_address)
        self.name = name
        self.plc_address_string = plc_address # e.g. IX0.0

        re_match = re.match(r"([IQ][XW])(\d{1,3})\.?(\d?)", self.plc_address_string)
        if not re_match:
            raise ValueError(f"Regex failed, invalid PLC Address {self.plc_address_string}")

        self.plc_address_type = re_match[1]
        self.plc_address = int(re_match[2])
        self._plc_address_count = re_match[3]  # not implemented
        self.is_binary = self.plc_address_type[1] == "X"

        max_value = int(max_value)
        if self.is_binary:
            message_size = self.BINARY_MESSAGE_SIZE
            if max_value == -1:
                max_value = 1
        else:
            message_size = self.ANALOG_MESSAGE_SIZE
            if max_value == -1:
                max_value = self.ANALOG_MESSAGE_SIZE

        self.max_value = max_value
        self.scaling_factor = message_size / self.max_value

    def __repr__(self):
        return f"{self.plc_address_string} ({self.iec104_address})"

    def message_encode(self, value: float) -> int:
        self.__validate_value(value)
        return round(value * self.scaling_factor)

    def message_decode(self, value: int) -> float:
        return value / self.scaling_factor

    def convert_value_iec104_to_modbus(self, value: float):
        pass

    def __validate_value(self, value: float):
        if value > self.max_value or value < 0:
            raise ValueError(f"point: {self} value: {value}, max_value: {self.max_value}")


class ReadPoint(Point):
    def __init__(self, **kwargs):
        self.pymodbus_read_method: str
        super().__init__(**kwargs)

        if self.plc_address_type == "QX":
            self.pymodbus_read_method = "read_coils"
        elif self.plc_address_type == "IX":
            self.pymodbus_read_method = "read_discrete_inputs"
        elif self.plc_address_type == "QW":
            self.pymodbus_read_method = "read_holding_registers"
        elif self.plc_address_type == "IW":
            self.pymodbus_read_method = "read_input_registers"
        else:
            raise ValueError(f"Not supported PLC Address type {self.plc_address_string}")

        if self.plc_address_type[1] == "X":
            self.pymodbus_value_property = "bits"
            self.c104_point_type = c104.Type.M_SP_NA_1  # Single-point information (1)
            self.default_value = False
        elif self.plc_address_type[1] == "W":
            self.pymodbus_value_property = "registers"
            self.c104_point_type = c104.Type.M_ME_NB_1  # Measured value, scaled value (11)
            self.default_value = 0

    def convert_value_iec104_to_modbus(self, value: float):
        return bool(value)  # TODO remove


class CommandPoint(Point):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.plc_address_type == "QX":
            self.pymodbus_command_method = "write_coil"
            self.c104_point_type = c104.Type.C_SC_NA_1  # Single command (45)
        elif self.plc_address_type == "QW":
            self.pymodbus_command_method = "write_register"
            self.c104_point_type = c104.Type.C_SE_NB_1  # Setpoint command, scaled value (49)
        else:
            raise ValueError(f"Not supported PLC Address type {self.plc_address_string}")

    def convert_value_iec104_to_modbus(self, value: float):
        return int(value)

def get_csv_file_reader():
    with open(os.path.dirname(__file__) + "/points.csv") as fh:
        reader = csv.reader(fh)
        rows  = list(reader)

    return rows

def get_csv_string_reader():
    csv_string: str  #REPLACE # This row is replaced by generate_psm_app.py with csv content.

    reader = csv.reader(csv_string.split("\n"))
    rows  = list(reader)

    return rows

def point_factory(csv_from: str = "file") -> Dict[str, Point]:
    # TODO validate csv by throwing exception if values are not unique
    points = {}

    if csv_from == "file":
        rows = get_csv_file_reader()
    elif csv_from == "string":
        rows = get_csv_string_reader()
    else:
        raise ValueError

    for row in rows[1:]:  # skip header
        assert row[0] in ["read", "command"]
        if row[0] == "read":
            points[row[2]] = ReadPoint(iec104_address = row[1], name = row[2], plc_address=row[3], max_value=row[4])
        elif row[0] == "command":
            points[row[2]] = CommandPoint(iec104_address = row[1], name = row[2], plc_address=row[3], max_value=row[4])

    return points
