import math
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
DEVICE = 8
RATE = 44100
RECORD_SECONDS = 5


p = pyaudio.PyAudio()
print("----------------------record device list---------------------")
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
print("USING ", DEVICE)
RATE = int(p.get_device_info_by_index(DEVICE)['defaultSampleRate'])
print(RATE)
print("-------------------------------------------------------------")
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=DEVICE,
                frames_per_buffer=CHUNK)



def rms(data_in):
    count = len(data_in) / 2
    format = "%dh"%(count)
    shorts = struct.unpack(format, data_in)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count ) * 1000



class Scope:
    def __init__(self, ax, maxt=2, dt=0.02):
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        self.ydata = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.line = Line2D(self.tdata, self.ydata, color="purple", fillstyle="full")
        self.ax.add_line(self.line)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, len(self.tdata))

    def update(self, y):
        self.ydata.pop(0)
        print("adding y ", y)
        print(self.ydata)
        self.ydata.append(y)
        self.line.set_data(self.tdata, self.ydata)
        return self.line,


def emitter(p=0.1):
    """Return a random value in [0, 1) with probability p, else 0."""
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        power = rms(data)
        yield power


plt.style.use('dark_background')
fig, ax = plt.subplots()
#ax.set_facecolor("black")
scope = Scope(ax)

try:
    # pass a generator in "emitter" to produce data for the update func
    ani = animation.FuncAnimation(fig, scope.update, emitter, interval=1000,
                                  blit=True, save_count=100)
    plt.show()
finally:
    print("closing alsa")
    stream.stop_stream()
    stream.close()
    p.terminate()
