"""Names and formats for known TECH params.

Names come from listener/decode.py and the Tech_RS-mqtt-gateway project. They
haven't all been checked against the EL-480's display yet.
"""

from collections import namedtuple

# The boiler sends the values it shares with both addresses identically, but only
# FFF4 carries the room readings, so it comes first.
PREFERRED_ADDRESSES = (0xFFF4, 0xFFFA)

# Names come from a forum post about other TECH controllers, except 0x02 and 0x52,
# which have been seen on this boiler. Unlisted codes are shown as raw hex.
STATE_NAMES = {0x02: "Working", 0x50: "Sustain", 0x52: "Supervision", 0x82: "Supervision"}
PUMP_MODES = {0: "House heating", 1: "Boiler priority", 2: "Parallel pumps",
              3: "Summer", 4: "Boiler priority"}
WEEKDAYS = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")


def signed(value):
    return value - 0x10000 if value & 0x8000 else value


def temp_tenths(value):
    return f"{signed(value) / 10:.1f} °C"


def temp_whole(value):
    return f"{value} °C"


def percent(value):
    return f"{value} %"


def on_off(value):
    return "On" if value else "Off"


def clock(value):
    return f"{value >> 8}:{value & 0xFF:02}"


def min_max(value):
    return f"{value & 0xFF}–{value >> 8} °C"


def weekday(value):
    return WEEKDAYS[value % 7]


def state(value):
    name = STATE_NAMES.get(value)
    return f"{name} (0x{value:02X})" if name else f"0x{value:02X}"


def pump_mode(value):
    return PUMP_MODES.get(value, str(value))


def fuel_level(value):
    return f"{value >> 9} %, {value & 0x1FF} kg"


def hours(value):
    return f"{value} h"


Reading = namedtuple("Reading", "group label selector param format")

READINGS = (
    Reading("Boiler", "Temperature", 0, 0x157D, temp_tenths),
    Reading("Boiler", "Setpoint", 0, 0x157E, temp_whole),
    Reading("Boiler", "Flue gas", 0, 0x15B7, temp_tenths),
    Reading("Boiler", "Feeder temperature", 0, 0x16F8, temp_tenths),
    Reading("Boiler", "Limits", 0, 0x169E, min_max),
    Reading("Boiler", "State", 0, 0x157C, state),

    Reading("Hot water", "Temperature", 0, 0x166E, temp_tenths),
    Reading("Hot water", "Setpoint", 0, 0x1616, temp_whole),
    Reading("Hot water", "Limits", 0, 0x169F, min_max),

    Reading("Room and outside", "Room", 1, 0x1699, temp_tenths),
    Reading("Room and outside", "Room setpoint", 1, 0x169A, temp_tenths),
    Reading("Room and outside", "Outside", 0, 0x1681, temp_tenths),

    Reading("Valve", "Temperature", 1, 0x1614, temp_tenths),
    Reading("Valve", "Setpoint", 1, 0x167F, temp_whole),
    Reading("Valve", "Open", 1, 0x15AC, percent),

    Reading("Outputs", "Fan", 0, 0x1588, on_off),
    Reading("Outputs", "Fan power", 0, 0x159B, percent),
    Reading("Outputs", "Feeder", 0, 0x1587, on_off),
    Reading("Outputs", "Heating pump", 0, 0x1589, on_off),
    Reading("Outputs", "Hot water pump", 0, 0x158B, on_off),
    Reading("Outputs", "Pump mode", 0, 0x15CD, pump_mode),

    Reading("Controller", "Clock", 0, 0x1620, clock),
    Reading("Controller", "Day", 0, 0x1621, weekday),
    Reading("Controller", "Fuel level", 0, 0x16F1, fuel_level),
    Reading("Controller", "Fuel time", 0, 0x16F2, hours),
)



def tenths_number(value):
    return signed(value) / 10


def binary_payload(value):
    return "ON" if value else "OFF"


MqttEntity = namedtuple("MqttEntity", "key name component selector param convert extras")

_TEMPERATURE = {"device_class": "temperature", "unit_of_measurement": "°C",
                "state_class": "measurement"}
_PERCENT = {"unit_of_measurement": "%", "state_class": "measurement"}
_RUNNING = {"device_class": "running"}

# Fuel level and the unknown params stay out until they're understood.
MQTT_ENTITIES = (
    MqttEntity("boiler_temperature", "Boiler temperature", "sensor", 0, 0x157D, tenths_number, _TEMPERATURE),
    MqttEntity("boiler_setpoint", "Boiler setpoint", "sensor", 0, 0x157E, int, _TEMPERATURE),
    MqttEntity("flue_temperature", "Flue gas temperature", "sensor", 0, 0x15B7, tenths_number, _TEMPERATURE),
    MqttEntity("feeder_temperature", "Feeder temperature", "sensor", 0, 0x16F8, tenths_number, _TEMPERATURE),
    MqttEntity("hot_water_temperature", "Hot water temperature", "sensor", 0, 0x166E, tenths_number, _TEMPERATURE),
    MqttEntity("hot_water_setpoint", "Hot water setpoint", "sensor", 0, 0x1616, int, _TEMPERATURE),
    MqttEntity("room_temperature", "Room temperature", "sensor", 1, 0x1699, tenths_number, _TEMPERATURE),
    MqttEntity("room_setpoint", "Room setpoint", "sensor", 1, 0x169A, tenths_number, _TEMPERATURE),
    MqttEntity("outside_temperature", "Outside temperature", "sensor", 0, 0x1681, tenths_number, _TEMPERATURE),
    MqttEntity("valve_temperature", "Valve temperature", "sensor", 1, 0x1614, tenths_number, _TEMPERATURE),
    MqttEntity("valve_setpoint", "Valve setpoint", "sensor", 1, 0x167F, int, _TEMPERATURE),
    MqttEntity("valve_open", "Valve open", "sensor", 1, 0x15AC, int, _PERCENT),
    MqttEntity("fan_power", "Fan power", "sensor", 0, 0x159B, int, _PERCENT),
    MqttEntity("boiler_state", "Boiler state", "sensor", 0, 0x157C, state, {}),
    MqttEntity("pump_mode", "Pump mode", "sensor", 0, 0x15CD, pump_mode, {}),
    MqttEntity("fan", "Fan", "binary_sensor", 0, 0x1588, binary_payload, _RUNNING),
    MqttEntity("feeder", "Feeder", "binary_sensor", 0, 0x1587, binary_payload, _RUNNING),
    MqttEntity("heating_pump", "Heating pump", "binary_sensor", 0, 0x1589, binary_payload, _RUNNING),
    MqttEntity("hot_water_pump", "Hot water pump", "binary_sensor", 0, 0x158B, binary_payload, _RUNNING),
)

# Names for the raw table, including params not shown as readings.
PARAM_NAMES = {
    0x01F6: "Boiler setpoint (from module)",
    0x01F9: "Room thermostat state",
    0x0225: "Cancel alarm",
    0x0245: "Pump mode (from module)",
    0x028E: "Hot water setpoint (from module)",
    0x0298: "Clock (from module)",
    0x0299: "Day (from module)",
    0x02F7: "Valve setting",
    0x02FC: "Boiler setpoint change",
    0x0311: "Room temperature (from room unit)",
    0x0312: "Room setpoint (from room unit)",
    0x0405: "Room setpoint",
    0x157C: "Boiler state",
    0x157D: "Boiler temperature",
    0x157E: "Boiler setpoint",
    0x1587: "Feeder on",
    0x1588: "Fan on",
    0x1589: "Heating pump",
    0x158B: "Hot water pump",
    0x159B: "Fan power",
    0x15A7: "Controller type",
    0x15AC: "Valve open",
    0x15B7: "Flue gas temperature",
    0x15CD: "Pump mode",
    0x1610: "Standby",
    0x1614: "Valve temperature",
    0x1616: "Hot water setpoint",
    0x1620: "Clock",
    0x1621: "Day of week",
    0x1624: "Valve type",
    0x166E: "Hot water temperature",
    0x167F: "Valve setpoint",
    0x1680: "Valve state",
    0x1681: "Outside temperature",
    0x1684: "Boiler temperature adjustment",
    0x1699: "Room temperature (inferred)",
    0x169A: "Room setpoint (inferred)",
    0x169E: "Boiler limits",
    0x169F: "Hot water limits",
    0x16C2: "Valve address",
    0x16C3: "Valve limits",
    0x16F1: "Fuel level",
    0x16F2: "Fuel time",
    0x16F8: "Feeder temperature",
    0x16FF: "Controller model",
    0x170A: "Valve adjustment",
}
