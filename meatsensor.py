# SPDX-License-Identifier: MIT
"""
    radar sensor for detecting human presence - part of outside voice

    This module is responsible for detecting human presence using a radar sensor.
    the user needs to have access to the serial device:

    sudo usermod -a -G dialout username

    this will allow the user to access the serial device without root privileges.

    The module reads data from the serial port and publishes it to the MQTT broker as `eventq`




"""

import json
import serial
import paho.mqtt.client as mqtt
import loguru
from loguru import logger

logger.add("meatsensor.log")
# mqtt boilerplate
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# client.on_connect = on_connect
# client.on_message = on_message
client.connect("localhost")
client.loop_start()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        logger.info("mqtt connected")


def read_from_serial(port="/dev/ttyACM0", baudrate=9600, timeout=1):
    """
    Reads data from the specified serial port.

    Args:
        port (str): The serial port name (default: '/dev/ttyACM0').
        baudrate (int): The baud rate of the serial communication (default: 9600).
        timeout (float): Read timeout in seconds (default: 1).

    Returns:
        str: The data read from the serial port, or None if no data is available.
    """

    try:
        # Open the serial port
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            # Read data from the port (adjust reading method as needed)
            data = ser.readline()
            return data
    except serial.SerialException as e:
        loguru.logger.warning(f"Error opening serial port: {e}")
        return None
    except UnicodeDecodeError:
        loguru.logger.warning(
            "Error decoding data from serial port. Check encoding settings."
        )
        return None


# Example usage
while True:
    data = read_from_serial()
    if data:
        loguru.logger.warning("Human sighted")
        client.publish("eventq", json.dumps({"value": "hooman sighted"}))
