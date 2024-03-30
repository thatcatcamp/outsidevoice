import hashlib
import json
import math
import struct
import subprocess
import pyaudio
import pygame
import os
import random
import time
import logging
from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Process
from dotenv import load_dotenv

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
]


def get_or_default(value, default):
    if os.getenv(value) is None:
        return default
    return os.getenv(value)


load_dotenv()
pygame.init()
SCREEN_WIDTH = 150
SCREEN_HEIGHT = 350
FIRE_SIZE = 15
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (0, 0)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
LAST_HASH = ""
pygame.display.set_caption("OutsideVoice")
FPS = 20
clock = pygame.time.Clock()
PECKER_MODE = True
PECKER_OVER = 0
NOISE_FLOOR = int(get_or_default("NOISE_FLOOR", 110))
CURRENT_BACKGROUND = "unknown"


def drift_one(ratio):
    print(ratio, NOISE_FLOOR)
    if ratio < NOISE_FLOOR:
        return 2
    return int(abs(math.sin(time.time() / 22)) * 255)


def drift_two(ratio):
    print(ratio, NOISE_FLOOR)
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


def draw_game_over_screen():
    global LAST_HASH, CURRENT_BACKGROUND
    max_in_pool = 0
    hf = hashlib.md5()
    hf.update(json.dumps(SAMPLES).encode("utf-8"))
    sum = hf.hexdigest()
    # reduce screen flicker
    if sum == LAST_HASH:
        return
    LAST_HASH = sum
    for i in range(len(SAMPLES)):
        if SAMPLES[i] > max_in_pool:
            max_in_pool = SAMPLES[i]
    number_samples = len(SAMPLES)
    each_height = SCREEN_HEIGHT / number_samples
    if CURRENT_BACKGROUND != "bars":
        screen.fill((0, 0, 0))
        CURRENT_BACKGROUND = "bars"
    for i in range(number_samples):
        ratio = SAMPLES[i]
        color = (ratio, drift_one(ratio), drift_two(ratio), i)
        # data is 0-255 for sample of voice (byte)
        width = SCREEN_WIDTH * (255 / SAMPLES[i])
        pygame.draw.rect(screen, color, (0, i * each_height, width, each_height))
        pygame.display.update()


MODE = "running"


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
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    DEVICE = 7
    RATE = 44100
    RECORD_SECONDS = 5

    start = time.time()
    p = pyaudio.PyAudio()
    print("----------------------record device list---------------------")
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get("deviceCount")
    for i in range(0, numdevices):
        if (
            p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")
        ) > 0:
            print(
                "Input Device id ",
                i,
                " - ",
                p.get_device_info_by_host_api_device_index(0, i).get("name"),
            )
            print(p.get_device_info_by_host_api_device_index(0, i))
            if (
                p.get_device_info_by_host_api_device_index(0, i).get("name")
                == "default"
            ):
                DEVICE = i
            channels = p.get_device_info_by_host_api_device_index(0, i).get(
                "maxInputChannels"
            )
            print("opening ...", channels)
            try:
                stream = p.open(
                    format=FORMAT,
                    channels=1,
                    rate=RATE,
                    input=True,
                    input_device_index=DEVICE,
                    frames_per_buffer=CHUNK,
                )
                for q in range(10):
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    the_sample = rms(data)
                    print(i, the_sample)
                    time.sleep(1)
            except OSError as e:
                print("Failed to open device ", e)

    # DEVICE = 4
    if os.path.exists("production.txt"):
        DEVICE = 6
    else:
        NOISE_FLOOR = 10
    DEVICE = int(get_or_default("DEVICE", DEVICE))
    print("USING ", DEVICE)

    RATE = int(p.get_device_info_by_index(DEVICE)["defaultSampleRate"])
    print(RATE)
    exit(1)
    print("-------------------------------------------------------------")
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=DEVICE,
        frames_per_buffer=CHUNK,
    )
    last_sample = 0
    never = 0xFFFFFFFF
    in_attract_mode_since = never
    rotate_attract = 60
    #    p1 = Process(target=playing_audio, args=())
    #    p1.start()
    playing_audio()
    while True:
        events = pygame.event.get()
        check_events(events)
        if time.time() - last_sample > 1:
            last_sample = time.time()
            data = stream.read(CHUNK, exception_on_overflow=False)
            the_sample = rms(data)
            SAMPLES.pop(0)
            #            print("push ", the_sample)
            # append new level sound level
            SAMPLES.append(the_sample)
            global MODE
            if empty_queue():
                MODE = "attract"
                if in_attract_mode_since == never:
                    in_attract_mode_since = time.time()
            else:
                MODE = "running"
                in_attract_mode_since = never
            start = time.time()
        if MODE == "attract":
            CURRENT_BACKGROUND = "attract"
            if in_attract_mode_since == never:
                screen.fill((random.randint(2, 255), 2, 2))
                print("clearing background")
                in_attract_mode_since = time.time()
            if (
                in_attract_mode_since != never
                and time.time() - in_attract_mode_since > rotate_attract
            ):
                screen.fill((random.randint(2, 255), 2, 2))
                in_attract_mode_since = time.time()
                print("rotating background")
            flame.draw_flame()
            pygame.display.update()
            clock.tick(FPS)
        else:
            draw_game_over_screen()
            clock.tick(5)


main_window()
