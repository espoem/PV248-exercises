import os
import sys
import wave
from collections import defaultdict
from math import log2

import numpy as np

PITCHES = ["c", "cis", "d", "es", "e", "f", "fis", "g", "gis", "a", "bes", "b"]


def octave_str(pitch, octave):
    if octave < 3:
        return pitch.title() + "," * (2 - octave)
    else:
        return pitch + "'" * (octave - 3)


def get_pitch(frequency, default_frequency):
    C0 = default_frequency * pow(2, -4.75)

    h = 12 * log2(frequency / C0)
    octave = int(h // 12)
    pitch = int(h % 12)
    cents = round((h % 1) * 100)

    if cents >= 50:
        pitch += 1
        cents = cents - 100
    elif cents < -50:
        pitch -= 1
        cents += 100

    pitch_str = octave_str(PITCHES[pitch], octave) + ("+" if cents >= 0 else "") + str(cents)
    return pitch_str


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 3:
        print("Wrong number of parameters")
        exit(1)

    default_freq = float(args[1])
    fp = args[2]

    # default_freq = 440
    # fp = 'Stereo_1000_80.wav'
    # fp = "t2.wav"
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

    # get peaks from each window
    peaks = []
    step = int(framerate * 0.1)
    for w in range(0, len(samples) - framerate, step):
        data = samples[w : w + framerate]
        amplitudes = np.abs(np.fft.rfft(a=data))
        mean = np.mean(amplitudes)
        peaks_aux = defaultdict(lambda: 0)
        for frq, a in enumerate(amplitudes.flat):
            if a >= 20 * mean:
                peaks_aux[frq] = a

        # print(peaks_aux)
        if not peaks_aux:
            continue
        for i in range(3):
            peaks_candidates = sorted(
                peaks_aux.items(), key=lambda kv: kv[1], reverse=True
            )[:3]
            try:
                del peaks_aux[peaks_candidates[i][0] + 1]
            except:
                pass
            try:
                del peaks_aux[peaks_candidates[i][0] - 1]
            except:
                pass

            # print(i, peaks_candidates)
            # print(peaks_aux)
        peaks_window = sorted(peaks_aux.items(), key=lambda kv: kv[1], reverse=True)[:3]
        peaks_window = [p[0] for p in peaks_window]
        peaks.append(sorted(peaks_window))
        # print(peaks_window)

    # convert peaks to pitches
    window_start = 0
    window_end = 0
    pitches = []
    for t, peak in enumerate(peaks):
        if t > 0:
            if set(peak) != set(peaks[t - 1]):
                print(
                    "{:.1f}-{:.1f} {}".format(
                        window_start, window_end, " ".join(pitches)
                    )
                )
                window_start = window_end
                pitches = [get_pitch(frequency, default_freq) for frequency in peak]
        else:
            pitches = [get_pitch(frequency, default_freq) for frequency in peak]
        window_end += 0.1

    if pitches:
        print("{:.1f}-{:.1f} {}".format(window_start, window_end, " ".join(pitches)))
