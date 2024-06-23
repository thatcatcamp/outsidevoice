# inhibits the spew from the pocketsphinx library
import json
import time

import sounddevice
import speech_recognition as sr
import paho.mqtt.client as mqtt
from loguru import logger

logger.add("sphinx.log")
# mqtt boilerplate
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# client.on_connect = on_connect
# client.on_message = on_message
client.connect("localhost")
client.loop_start()
"""
    this is a light version of the AI spy that works
    with the pocketsphinx library. It listens for 5 seconds
"""
# Create a recognizer instance
r = sr.Recognizer()
logger.info("cold booting spy")
# Use the default microphone as the audio source
while True:
    # if /tmp/powersave.flg exists - sleep then loop
    # decoding is CPU hungry
    try:
        with open("/tmp/powersave.flg", "r") as f:
            logger.info("powersave mode enabled")
            time.sleep(20)
            continue
    except FileNotFoundError:
        pass
    with sr.Microphone() as source:
        audio_data = r.record(source, duration=10)
        # Convert the audio to text
        try:
            text = r.recognize_sphinx(audio_data)
            if text == "":
                continue
            logger.info("heard: ", text)
            client.publish("eventq", json.dumps({"value": text}))
        except sr.UnknownValueError:
            logger.warning("PocketSphinx could not understand the audio")
        except sr.RequestError as e:
            logger.warning(
                "Could not request results from PocketSphinx service; {0}".format(e)
            )
