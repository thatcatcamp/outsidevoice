import math
import struct

import numpy as np
import pyaudio
from matplotlib import animation as animation, pyplot as plt, cm

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
DEVICE = 7
RATE = 44100
RECORD_SECONDS = 5
DATA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print(len(DATA))
# exit(1)
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
print("-------------------------------------------------------------")
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=DEVICE,
    frames_per_buffer=CHUNK,
)


def rms(data_in):
    count = len(data_in) / 2
    format_g = "%dh" % count
    shorts = struct.unpack(format_g, data_in)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    return math.sqrt(sum_squares / count) * 1000


plt.style.use("dark_background")

plt.rcParams["figure.figsize"] = [17.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig = plt.figure()

data = range(20)
colors = ["red", "yellow", "blue", "green", "black"]
bars = plt.bar(data, data, facecolor="purple", alpha=0.75)


def amp_to_color(power):
    power = power * 100
    if power > 255:
        power = 255
    return "#%02x0d010d" % int(power)


#    return f"#0d01{hex(int(power)).lstrip('0x').rstrip('L')}"


def animate(frame):
    global bars, data

    index = np.random.randint(1, 7)
    data_in = stream.read(CHUNK, exception_on_overflow=False)
    power = rms(data_in)
    print("powah ", power, " ", amp_to_color(power))
    for x in data:
        if x == 0:
            continue
        DATA[x - 1] = DATA[x]
        bars[x - 1].set_height(DATA[x])
        bars[x - 1].set_color(amp_to_color(DATA[x]))
    bars[len(data) - 1].set_height(power)
    bars[len(data) - 1].set_color(amp_to_color(power))
    DATA[len(DATA) - 1] = power


#    data.pop(0)
#    data.append(power)


ani = animation.FuncAnimation(fig, animate, frames=len(data))

plt.show()
