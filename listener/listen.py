#!/usr/bin/env python3

from serial import Serial
import paho.mqtt.publish as publish

MQTT_SERVER_IP = "localhost"
MQTT_SERVER_PORT = 1883
MQTT_USER_NAME = "home"
MQTT_PASSWORD = "home123"
MQTT_TOPIC = "heating_raw/boiler_data"

with Serial("/dev/ttyACM0", 115200, timeout=0.001) as port:

    while 1:
        lines = port.readlines()
        try:
            for line in lines:
                pre, data = line.decode('ascii').split(':')
                pre = pre.strip().split()[1][-1]
                data = data.strip().split()
                msg = '{}'.format(pre)
                for d in data:
                    msg += d
                publish.single(topic=MQTT_TOPIC, payload=msg,
                               auth={'username': MQTT_USER_NAME, 'password': MQTT_PASSWORD},
                               port=MQTT_SERVER_PORT, hostname=MQTT_SERVER_IP)
        except ValueError:
            pass