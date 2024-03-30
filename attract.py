import curses
import math
import os
import random
import struct
import time
from curses import wrapper
import pyaudio
import traceback
from colorama import Fore, Back, Style
import pyaudio
import wave
from playsound import playsound

MODE = "running"

X = [Back.RED, Back.BLUE, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE]
BLANK = {"s": "▢▢▢▢▢▢", "c": 1}
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
COLORS = [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
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


def play_sound(this_sound: str):
    os.system(f"aplay -c 2 -f S16_LE -D hw:0,0 {this_sound}")


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


def push_it():
    choices = [
        "▀▀▀▀▀▀▀▀",
        "▄▄▄▄▄▄▄▄",
        "▅▅▅▅▅▅▅▅",
        "▆▆▆▆▆▆▆▆",
        "▇▇▇▇▇▇▇▇",
        "████████",
        "░░░░░░░░",
        "▒▒▒▒▒▒▒▒",
        "▓▓▓▓▓▓▓▓",
    ]
    new_one = {"s": random.choice(choices), "c": random.randint(0, 9)}
    SAMPLES.pop(0)
    SAMPLES.append(new_one)


def paint_color(stdscr):
    line = 0
    stdscr.clear()
    #    debug = open("debug.log", "w+t")
    for i in SAMPLES:
        if i is not None:
            try:
                stdscr.addstr(line, 0, i["s"], curses.color_pair(i["c"]))
            #                debug.print_str(f"{line} ok")
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


#   debug.close()


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
    #    curses.init_pair(0, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)

    stdscr.clear()
    debug = open("debug.log", "w+t")
    while True:
        new_color = random.randint(1, 7)
        try:
            push_it()
            debug.write(f"{SAMPLES}\n")
            paint_color(stdscr)
            next_sound = random.choice(
                [
                    "c0.mp3",
                    "c1.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                    "m.wav",
                ]
            )
            if random.randint(0, 99) > 95:
                next_sound = "modem.wav"

            play_sound(next_sound)
        except TypeError as e:
            debug.write("unexpected TypeError " + str(e) + "\n")
            traceback.print_exc()
            pass
        stdscr.refresh()
        time.sleep(1)


wrapper(main)

"""
COLOR_BLUE = 4
COLOR_CYAN = 6
COLOR_GREEN = 2
COLOR_MAGENTA = 5
COLOR_RED = 1
COLOR_WHITE = 7
COLOR_YELLOW = 3
"""
