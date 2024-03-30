import curses
import math
import os
import struct
import time
from curses import wrapper
import random
import pyaudio
import traceback
from colorama import Fore, Back, Style

MODE = "running"

X = [Back.RED, Back.BLUE, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE]
BLANK = 0.1
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
MIN_LEVEL = 15.0
OUT_OF_LEVEL = "-"


def empty_queue():
    global OUT_OF_LEVEL
    loop = 0
    with open("queue.log", "w+") as ql:
        ql.write(f"{SAMPLES}\n")
        for i in SAMPLES:
            if i > MIN_LEVEL:
                ql.write(f"hot data @ {i} / {loop}\n")
                OUT_OF_LEVEL = f"{i} > {MIN_LEVEL} @ level {loop} {SAMPLES}"
                return False
            loop = loop + 1
        ql.write(f"returning TRUE\n")
        return True


def play_sound(this_sound: str):
    os.system(f"aplay -c 2 -f S16_LE -D hw:0,0 {this_sound}")


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
        out = Fore.WHITE + Style.BRIGHT
    return out + f"{level}"


def level_up(level: float):
    if level < 20:
        return 1
    if level < 80:
        return 2
    if level < 120:
        return 3
    if level < 150:
        return 4
    return 5


def level_print(level: float):
    global MODE

    if level < 20:
        return f"▢▢▢▢▢▢\t{level}"
    if level < 80:
        return f"▢▢▢▢▢▢\t{level}"
    if level < 120:
        return f"▢▢▢▢▢▢\t{level}"
    if level < 150:
        return f"▢▢▢▢▢▢\t{level}"
    return f"◼◼◼◼◼◼\t{level}"


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
    #    level_to_string(level)
    return min(level, 255)


def paint(stdscr):
    line = 0
    stdscr.clear()
    for i in SAMPLES:
        if i is not None:
            try:
                stdscr.addstr(line, 0, level_print(i), curses.color_pair(level_up(i)))
            except curses.error as e:
                print(e)
        else:
            stdscr.addstr(
                line,
                0,
                f"{line} nil? {len(SAMPLES)}",
                curses.color_pair(level_up(0.00)),
            )
        line = line + 1
    stdscr.refresh()


def paint_color(this_color, stdscr):
    line = 0
    stdscr.clear()
    for i in SAMPLES:
        if i is not None:
            try:
                stdscr.addstr(line, 0, level_print(i), curses.color_pair(this_color))
            except curses.error as e:
                print(e)
        else:
            stdscr.addstr(
                line,
                0,
                f"{line} nil? {len(SAMPLES)}",
                curses.color_pair(level_up(0.00)),
            )
        line = line + 1
    stdscr.refresh()


if os.path.exists("production.txt"):
    DEVICE = 6

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


def main(stdscr):
    # Clear screen
    global MODE
    global OUT_OF_LEVEL
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

    stdscr.clear()
    debug = open("debug.log", "w+t")
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        # pop old
        data_point = rms(data)
        popped = SAMPLES.pop(0)
        debug.write(f"popped {popped}\n")
        debug.write(f"push {data_point}\n")
        debug.write(f"{SAMPLES}\n")
        debug.flush()
        # append new level sound level
        SAMPLES.append(data_point)
        if empty_queue():
            MODE = "attract"
            OUT_OF_LEVEL = "-"
        else:
            MODE = "running"
        try:
            if MODE == "attract":
                new_color = random.randint(1, 7)
                paint_color(new_color, stdscr)
            else:
                paint(stdscr)
        except TypeError as e:
            print("unexpected TypeError " + str(e))
            traceback.print_exc()
            pass
        stdscr.refresh()
        time.sleep(1)


wrapper(main)
