import math
import os
import struct
import time

import curses
import pyaudio
from colorama import Fore, Back, Style

MODE = "running"

X = [Back.RED, Back.BLUE, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE]
BLANK = Back.BLACK + "-----"
SAMPLES = [
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
    BLANK,
]
SCREEN_WIDTH = 150
SCREEN_HEIGHT = 650

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
DEVICE = 7
RATE = 44100
RECORD_SECONDS = 5


def empty_queue():
    for i in SAMPLES:
        if i != BLANK:
            print("QUEUE IS NOT EMPTY")
            return False
    return True


def level_to_string(level: float):
    out = Back.WHITE
    if level < 150:
        out = Back.LIGHTRED_EX + Style.BRIGHT
    if level < 120:
        out = Back.YELLOW + Style.BRIGHT
    if level < 80:
        out = Back.GREEN + Style.DIM
    if level < 20:
        out = Back.LIGHTBLACK_EX + Style.DIM
    if level > 200:
        out = Back.WHITE + Style.BRIGHT
    return out + f"{level}"


#    print(out + f"{level}")


def rms(data_in):
    count = len(data_in) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, data_in)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    level = math.sqrt(sum_squares / count) * 9000
    level_to_string(level)
    return level_to_string(min(level, 255))


def paint():
    for i in SAMPLES:
        print(i)


if os.path.exists("production.txt"):
    DEVICE = 5

start = time.time()
p = pyaudio.PyAudio()
print("----------------------record device list---------------------")
info = p.get_host_api_info_by_index(0)
numdevices = info.get("deviceCount")
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0:
        print(
            "Input Device id ",
            i,
            " - ",
            p.get_device_info_by_host_api_device_index(0, i).get("name"),
        )
print("USING ", DEVICE)
RATE = int(p.get_device_info_by_index(DEVICE)["defaultSampleRate"])
print(RATE)
print(Style.RESET_ALL)
print("-------------------------------------------------------------")
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=DEVICE,
    frames_per_buffer=CHUNK,
)
while True:
    data = stream.read(CHUNK, exception_on_overflow=False)
    # pop old
    SAMPLES.pop(0)
    # append new level sound level
    SAMPLES.append(rms(data))
    if time.time() - start > 2:
        if empty_queue() and MODE == "running":
            MODE = "attract"
        else:
            MODE = "running"
        start = time.time()
    paint()
    time.sleep(1)
"""    if MODE == "attract":
        screen.fill((0, 0, 0))
        flame.draw_flame()
        pygame.display.update()
        clock.tick(FPS)
    else:
        draw_game_over_screen()
        clock.tick(1)

while True:
    for c in X:
        print(c + "porklet")
"""


def main(stdscr):
    # Clear screen
    stdscr.clear()

    # This raises ZeroDivisionError when i == 10.
    for i in range(0, 11):
        v = i - 10
        stdscr.addstr(i, 0, "10 divided by {} is {}".format(v, 10 / v))

    stdscr.refresh()
    stdscr.getkey()


curses.wrapper(main)
