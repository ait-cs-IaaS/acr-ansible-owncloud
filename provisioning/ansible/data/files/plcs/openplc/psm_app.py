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

        max_value = int(max_value)
        if self.plc_address_type[1] == "X":  # if binary
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
    csv_string = """message_type,iec104_address,name,modbus_address,max_value
read,11,power,IW0,16384000
read,12,target_power,IW1,16384000
read,13,field_current,IW2,600
read,14,flow_rate,IW3,100
read,15,generator_velocity,IW4,2000
read,16,grid_voltage,IW5,40000
read,17,grid_frequency,IW6,70
read,18,shutdown,IX0.0,-1
command,31,target_power_command,QW0,16384000
command,30,shutdown_command,QX0.0,-1"""
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

points = point_factory(csv_from="string")

import math
import os
import psm  # when run outside OpenPLC runtime, this is mocked by psm.py
import random
import time

max_modbus_value = pow(2,15)

# constants
VOLTAGE = 20_000  # v (Volts)
WATER_DENSITY = 1000  # ρ (kg/m^3)
GRAVITY = 9.81  # g (m/s^2)
WATERFALL_HEIGHT = 15  # H (meters)
GLOBAL_EFFICIENCY_RATIO = 0.85  # η (%)
GRID_FREQUENCY = 50  # Hz


class Transition:
    max_steps = 250  # TODO make this a function of the rate of change

    def __init__(self, start: int, target: int):
        self.start = start
        self.target = target
        self.step = 0

        # sinus transition from 0 to 1
        self.multipliers = [math.sin(x / ((self.max_steps-1) / math.pi) - math.pi/2) / 2 + 0.5 for x in range(self.max_steps)]

    def get_value(self):
        if self.step >= self.max_steps:
            return self.target

        value = self.start + (self.target - self.start) * self.multipliers[self.step]
        self.step += 1

        return value


def add_noise(value: float, max_deviation = 0.01) -> float:
    max_deviation = value * max_deviation

    noise = random.uniform(max_deviation * -1, max_deviation)
    return max(value + noise, 0.0)

def get_field_current(_power: float) -> float:
    return _power / VOLTAGE

def get_flow_rate(_power: float) -> float:  # Q (m^3/s)
    return _power / (WATER_DENSITY * GRAVITY * WATERFALL_HEIGHT * GLOBAL_EFFICIENCY_RATIO)

def update_inputs():
    global power, target_power_old, target_power_new, power_transition, generator_velocity, generator_velocity_transition, shutdown

    if not shutdown:
        shutdown_command = psm.get_var(points["shutdown_command"].plc_address_string)
        shutdown_command = points["shutdown_command"].message_decode(shutdown_command)

        if shutdown_command:
            shutdown = 1
            power_transition = Transition(power, 0)
            generator_velocity_transition = Transition(generator_velocity, 0)

        else:
            maybe_target_power_new = psm.get_var(points["target_power_command"].plc_address_string)
            # TODO we may not need to cast to int after all!
            maybe_target_power_new = points["target_power_command"].message_decode(maybe_target_power_new)

            if 0 < maybe_target_power_new != target_power_old:
                target_power_new = maybe_target_power_new
                power_transition = Transition(power, target_power_new)
                target_power_old = target_power_new

    power = power_transition.get_value()
    field_current = get_field_current(power)
    flow_rate = get_flow_rate(power)

    generator_velocity = generator_velocity_transition.get_value()

    power = add_noise(power)
    field_current = add_noise(field_current)
    flow_rate = add_noise(flow_rate)
    grid_voltage = add_noise(VOLTAGE, 0.001)
    generator_velocity_noisy = add_noise(generator_velocity, 0.001)
    grid_frequency = add_noise(GRID_FREQUENCY, 0.001)

    # TODO we may not need to cast to int after all!
    modbus_power = points["power"].message_encode(power)
    modbus_target_power = points["target_power"].message_encode(target_power_new)
    modbus_field_current = points["field_current"].message_encode(field_current)
    modbus_flow_rate = points["flow_rate"].message_encode(flow_rate)
    modbus_grid_voltage = points["grid_voltage"].message_encode(grid_voltage)
    modbus_generator_velocity = points["generator_velocity"].message_encode(generator_velocity_noisy)
    modbus_grid_frequency = points["grid_frequency"].message_encode(grid_frequency)
    modbus_shutdown = points["shutdown"].message_encode(shutdown)

    psm.set_var(points["power"].plc_address_string, modbus_power)
    psm.set_var(points["target_power"].plc_address_string, modbus_target_power)
    psm.set_var(points["field_current"].plc_address_string, modbus_field_current)
    psm.set_var(points["flow_rate"].plc_address_string, modbus_flow_rate)
    psm.set_var(points["grid_voltage"].plc_address_string, modbus_grid_voltage)
    psm.set_var(points["generator_velocity"].plc_address_string, modbus_generator_velocity)
    psm.set_var(points["grid_frequency"].plc_address_string, modbus_grid_frequency)
    psm.set_var(points["shutdown"].plc_address_string, modbus_shutdown)


if __name__ == "__main__":
    psm.start()

    # initial values
    power = 1_000_000  # P (Watts)
    generator_velocity = 1500  # rpm
    target_power_old = power
    target_power_new = power
    power_transition = Transition(power, power)
    generator_velocity_transition = Transition(generator_velocity, generator_velocity)
    shutdown = 0

    while not psm.should_quit():
        update_inputs()
        if os.environ.get("SHIFT_DEBUG") != "1":
            time.sleep(0.1)  # You can adjust the psm cycle time here
    psm.stop()

# https://openplcproject.com/docs/2-5-modbus-addressing/
# TODO check path /workdir/webserver/./core/psm/main.py to see if helps with proper dockerization
# TODO implement shutdown
# TODO implement other variables
