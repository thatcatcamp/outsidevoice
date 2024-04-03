#!/usr/bin/python3
import json
import math
import struct
import subprocess
import pyaudio
import paho.mqtt.client as mqtt
import pygame
import os
import random
import time
import logging
import socket
from dotenv import load_dotenv
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw

butt_image = pygame.image.load("butt.jpg")
mbutt_image = pygame.image.load("mbutts.jpg")
cat_image = pygame.image.load("cat.jpg")
sheep_image = pygame.image.load("sheep.jpg")
rick_image = pygame.image.load("rick.jpg")
bacon_image = pygame.image.load("bacon.jpg")
screen = None
SLOGANS = [
    "MOAR BOOBS",
    "OBEY CAT",
    "MOAR BOOKS",
    " EAT TOFU ",
    "ROBOT HEART IS FOR ROBOTS",
    "STINKY HOOMANS",
    "CLIPPY HAS THE ANSWERS",
]
ADS = {}
# Set the path for the Unix socket
socket_path = "/tmp/voice.socket"
# remove the socket file if it already exists
try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise


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
    # userdata is the structure we choose to provide, here it's a list()
    print(message.payload)
    try:
        exploded = json.loads(message.payload)

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
        img = Image.open("blank.jpg")
        fs = round(10 / (len(s)) * 36, 0)

        print(fs)
        font = ImageFont.truetype("spacemono.ttf", int(fs))
        txt = Image.new("L", (250, 71))
        d = ImageDraw.Draw(txt)
        d.text((10, 10), s, font=font, fill=255)
        w = txt.rotate(90, expand=True)
        img.paste(w)
        img.save("out.jpg")
        ADS[s] = pygame.image.load("out.jpg")


def fight_club(x, y):
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

SAMPLES = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
]


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
PECKER_MODE = True
PECKER_OVER = 0
NOISE_FLOOR = int(get_or_default("NOISE_FLOOR", 110))
CURRENT_BACKGROUND = "unknown"


def drift_one(ratio):
    # print(ratio, NOISE_FLOOR)
    if ratio < NOISE_FLOOR:
        return 2
    return int(abs(math.sin(time.time() / 22)) * 255)


def drift_two(ratio):
    # print(ratio, NOISE_FLOOR)
    if ratio < NOISE_FLOOR:
        return 2
    return int(abs(math.sin(time.time() / 45)) * 255)


class FlameParticle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 2

    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 4, r=15):
        self.x = x
        self.y = y
        self.r = r
        self.original_r = r
        self.alpha_layers = FlameParticle.alpha_layer_qty
        self.alpha_glow = FlameParticle.alpha_glow_difference_constant
        max_surf_size = (
            2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        )
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        self.burn_rate = 0.01 * random.randint(1, 10)

    def update(self):
        self.y -= 7 - self.r
        self.x += random.randint(-self.r, self.r)
        self.original_r -= self.burn_rate
        self.r = int(self.original_r)
        if self.r <= 0:
            self.r = 1

    def draw(self):
        max_surf_size = (
            2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        )
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - i * (255 // self.alpha_layers - 5)
            if alpha <= 0:
                alpha = 0
            radius = self.r * i * i * self.alpha_glow
            if self.r == 4 or self.r == 3:
                r, g, b = (255, 0, 255)
            elif self.r == 2:
                r, g, b = (255, 150, 0)
            else:
                r, g, b = (59, 7, 57)
            # r, g, b = (0, 0, 255)  # uncomment this to make the flame blue
            color = (r, g, b, alpha)
            pygame.draw.circle(
                self.surf,
                color,
                (self.surf.get_width() // 2, self.surf.get_height() // 2),
                radius,
            )
        screen.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))


class Flame:
    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT * 0.9):
        self.x = x
        self.y = y
        self.flame_intensity = 1
        self.flame_particles = []
        for i in range(self.flame_intensity * 25):
            self.flame_particles.append(
                FlameParticle(
                    self.x + random.randint(-1 * FIRE_SIZE, FIRE_SIZE),
                    self.y,
                    random.randint(1, FIRE_SIZE),
                )
            )

    def draw_flame(self):
        for i in self.flame_particles:
            if i.original_r <= 0:
                self.flame_particles.remove(i)
                self.flame_particles.append(
                    FlameParticle(
                        self.x + random.randint(-1 * FIRE_SIZE, FIRE_SIZE),
                        self.y,
                        random.randint(1, FIRE_SIZE),
                    )
                )
                del i
                continue
            i.update()
            i.draw()


flame = Flame()


MODE = "attact"


def playing_audio():
    global PECKER_MODE, PECKER_OVER
    # this is 21 seconds long
    PECKER_MODE = True
    PECKER_OVER = time.time() + 21
    subprocess.Popen(["aplay", "w.wav"])


def rms(data_in):
    global PECKER_MODE, PECKER_OVER
    count = len(data_in) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, data_in)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    level = math.sqrt(sum_squares / count) * 9000
    if level > 0:
        print("rms level:", level)
        logging.debug("level {} ".format(level))
    if PECKER_MODE:
        if time.time() > PECKER_OVER:
            PECKER_MODE = False
        return abs(math.sin(time.time())) * 255
    return max(min(level, 255), 1)


def check_events(events):
    for e in events:
        if e.type == pygame.QUIT:
            quit()


def empty_queue():
    for i in SAMPLES:
        if i > NOISE_FLOOR:
            #            print("QUEUE IS NOT EMPTY")
            return False
    return True


def main_window():
    global NOISE_FLOOR, CURRENT_BACKGROUND
    rotate_attract = 60
    never = 0xFFFFFFFF
    in_attract_mode_since = never
    #    p1 = Process(target=playing_audio, args=())
    #    p1.start()
    # playing_audio()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    server.setblocking(False)
    server.listen(1)
    while True:
        events = pygame.event.get()
        mqttc.loop(timeout=0)
        try:
            c, a = server.accept()
            print("Connection from", c)
            the_data = c.recv(1024)
            print("msg ", the_data)
        except BlockingIOError:
            pass
        check_events(events)
        if True:
            CURRENT_BACKGROUND = "attract"
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
            flame.draw_flame()
            pygame.display.update()
            clock.tick(FPS)
        else:
            clock.tick(5)


generate_images()
main_window()
