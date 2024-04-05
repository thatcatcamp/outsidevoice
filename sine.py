import array
import math
import time

import pyaudio

p = pyaudio.PyAudio()

volume = 0.5  # range [0.0, 1.0]
fs = 44100  # sampling rate, Hz, must be integer
duration = 5.0  # in seconds, may be float
f = 440.0  # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
num_samples = int(fs * duration)
samples = [volume * math.sin(2 * math.pi * k * f / fs) for k in range(0, num_samples)]

# per @yahweh comment explicitly convert to bytes sequence
output_bytes = array.array("f", samples).tobytes()

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)

# play. May repeat with different volume values (if done interactively)
start_time = time.time()
stream.write(output_bytes)
print("Played sound for {:.2f} seconds".format(time.time() - start_time))

stream.stop_stream()
stream.close()

p.terminate()
