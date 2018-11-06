import math
import os
import struct
import sys
import wave

import numpy as np

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Wrong number of parameters")
        exit(1)

    fp = args[1]
    here = os.path.dirname(__file__)
    wav_filepath = os.path.join(here, fp)
    with wave.open(wav_filepath, "rb") as wav:
        nframes = wav.getnframes()
        nchannels = wav.getnchannels()
        framerate = wav.getframerate()
        sampwidth = wav.getsampwidth()
        frames = np.frombuffer(wav.readframes(nframes), dtype=np.int16)

    samples = np.array(frames)

    if nchannels == 2:
        s = []
        for i in range(0, len(frames), 2):
            s.append(np.mean([frames[i], frames[i + 1]]))
        samples = np.array(s)

    p = 1
    n = framerate * p
    windows_count = nframes // n

    peaks = []
    for w in range(windows_count):
        start = w * n
        end = (w + 1) * n
        data = samples[start:end]
        mag = np.abs(np.fft.rfft(a=data))
        mean = np.mean(mag)
        for frq, p in enumerate(mag.flat):
            if p >= 20 * mean:
                peaks.append(frq)

    # print(peaks)
    if peaks:
        print("low = {}, high = {}".format(np.min(peaks), np.max(peaks)))
    else:
        print("no peaks")
