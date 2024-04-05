#!/usr/bin/python3
import datetime
import json
import math
import struct
import subprocess
import paho.mqtt.client as mqtt
import pygame
import os
import random
import time
import logging
from dotenv import load_dotenv
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

screen = None
SLOGANS = [
    "MOAR BOOBS",
    "OBEY CAT",
    "MOAR BOOKS",
    "VEGAN TAROT HERE",
    "VIP LOUNGE",
    "DISCOUNT HUGS",
    "CAT YOGA @ 13:33",
    "FREE DUST",
    "ASK FOR THE ANSWERS",
    "DON'T LISTEN TO CLIPPY",
    " EAT TOFU ",
    "ROBOT HEART IS FOR ROBOTS",
    "STINKY HOOMANS",
    "CLIPPY HAS THE ANSWERS",
]
ADS = {}
LAST_EVENT = 0
LAST_ROTATE = 0
SPY_TEXT = ""


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    print("on_unsubscribe")
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()


def on_message(client, userdata, message):
    global LAST_EVENT, SPY_TEXT
    # userdata is the structure we choose to provide, here it's a list()
    print(message.payload)
    try:
        exploded = json.loads(message.payload)
        LAST_EVENT = time.time()
        SPY_TEXT = exploded["value"]
    except Exception as e:
        print(e)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("eventq")


def generate_images():
    for s in SLOGANS:
        print("generate image for", s)
        img = Image.new(
            "L", (75, 400), random.randint(0, 255)
        )  # Image.open("blank.jpg")
        fs = round(10 / (len(s)) * 36, 0)

        print(fs)
        font = ImageFont.truetype("spacemono.ttf", int(fs))
        txt = Image.new("L", (350, 75), random.randint(0, 255))
        d = ImageDraw.Draw(txt)
        d.text((10, 10), s, font=font, fill=255)
        w = txt.rotate(90, expand=True)
        img.paste(w)
        img.save("out.jpg")
        ADS[s] = pygame.image.load("out.jpg")


def fight_club(x, y):
    global LAST_EVENT, SPY_TEXT, LAST_ROTATE
    if LAST_EVENT > LAST_ROTATE or LAST_ROTATE + 60 < time.time():
        LAST_ROTATE = time.time()
        print("ads -> ", len(ADS))
        screen.blit(
            ADS[random.choice(SLOGANS)],
            (x, y),
        )


logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def get_or_default(value, default):
    if os.getenv(value) is None:
        return default
    return os.getenv(value)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

mqttc.user_data_set([])
mqttc.connect("localhost")
load_dotenv()
pygame.init()
SCREEN_WIDTH = 75
SCREEN_HEIGHT = 350
FIRE_SIZE = 15
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (0, 0)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
LAST_HASH = ""
pygame.display.set_caption("OutsideVoice")
FPS = 20
clock = pygame.time.Clock()
NOISE_FLOOR = int(get_or_default("NOISE_FLOOR", 110))
MODE = "attact"


def check_events(events):
    for e in events:
        if e.type == pygame.QUIT:
            quit()


def main_window():
    global NOISE_FLOOR
    rotate_attract = 60
    never = 0xFFFFFFFF
    in_attract_mode_since = never
    while True:
        events = pygame.event.get()
        mqttc.loop(timeout=0)
        check_events(events)
        if in_attract_mode_since == never:
            screen.fill((random.randint(2, 255), 2, 2))
            fight_club(0, 1)
            print("clearing background")
            in_attract_mode_since = time.time()
        if (
            in_attract_mode_since != never
            and time.time() - in_attract_mode_since > rotate_attract
        ):
            screen.fill((random.randint(2, 255), 2, 2))
            fight_club(0, 1)
            in_attract_mode_since = time.time()
            print("rotating background")
        #            flame.draw_flame()
        pygame.display.update()
        clock.tick(FPS)


generate_images()
main_window()
