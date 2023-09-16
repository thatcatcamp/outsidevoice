# imports
import math
import struct
import matplotlib.pyplot as plt
import pyaudio
import ctypes
time_read = []
amplitude = []


# shows the sound waves
def visualize(path: str):
    plt.figure(1)
    plt.title("Sound Wave")
    plt.xlabel("Time")
    plt.plot(time_read, amplitude)




def rms(data_in):
    count = len(data_in) / 2
    format = "%dh"%(count)
    shorts = struct.unpack(format, data_in)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )


if __name__ == "__main__":
    # gets the command line Value
    for x in range(30):
        time_read.append(x)
        amplitude.append(0)
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

    print("* recording")
    print(p.get_device_count())
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        power = rms(data)
        for shift in range(len(amplitude)):
            if shift == 0:
                continue
            amplitude[shift-1] = amplitude[shift]
        amplitude[len(amplitude)-1] = power



    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    visualize("")
