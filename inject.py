#!/usr/bin/env python3
import json
import sys
import time

import sounddevice
import speech_recognition as sr
import paho.mqtt.client as mqtt
from loguru import logger

# mqtt boilerplate
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# client.on_connect = on_connect
# client.on_message = on_message
client.connect("localhost")
client.loop_start()
print(f"sending {sys.argv[1]} ")
client.publish("eventq", json.dumps({"value": sys.argv[1]}))
