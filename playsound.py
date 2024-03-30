import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
import time
from multiprocessing import Process


def playing_audio():
    song = AudioSegment.from_wav(wavFile)
    play(song)


def showing_audiotrack():
    # We use a variable previousTime to store the time when a plot update is made
    # and to then compute the time taken to update the plot of the audio data.
    previousTime = time.time()

    # Turning the interactive mode on
    plt.ion()

    # Each time we go through a number of samples in the audio data that corresponds to one second of audio,
    # we increase spentTime by one (1 second).
    spentTime = 0

    # Let's the define the update periodicity
    updatePeriodicity = 2  # expressed in seconds

    # Plotting the audio data and updating the plot
    for i in range(n):
        # Each time we read one second of audio data, we increase spentTime :
        if i // Fs != (i - 1) // Fs:
            spentTime += 1
        # We update the plot every updatePeriodicity seconds
        if spentTime == updatePeriodicity:
            # Clear the previous plot
            plt.clf()
            # Plot the audio data
            plt.plot(time_axis, sound_axis)
            # Plot a red line to keep track of the progression
            plt.axvline(x=i / Fs, color="r")
            plt.xlabel("Time (s)")
            plt.ylabel("Audio")
            plt.show()  # shows the plot
            plt.pause(updatePeriodicity - (time.time() - previousTime))
            # a forced pause to synchronize the audio being played with the audio track being displayed
            previousTime = time.time()
            spentTime = 0


# PREPARING THE AUDIO DATA

# Audio file, .wav file
wavFile = "w.wav"

# Retrieve the data from the wav file
data, samplerate = sf.read(wavFile)

n = len(data)  # the length of the arrays contained in data
Fs = samplerate  # the sample rate

# Working with stereo audio, there are two channels in the audio data.
# Let's retrieve each channel seperately:
print(len(data.transpose()))
ch1 = data  # data.transpose()

# x-axis and y-axis to plot the audio data
time_axis = np.linspace(0, n / Fs, n, endpoint=False)
sound_axis = ch1  # we only focus on the first channel here

# You can run the two lines below to plot the audio data contained in the audio file
# plt.plot(time_axis, sound_axis)
# plt.show()


if __name__ == "__main__":
    p1 = Process(target=playing_audio, args=())
    p1.start()
    p2 = Process(target=showing_audiotrack, args=())
    p2.start()
    p1.join()
    p2.join()
