import pyaudio
import sys
import time
import numpy as np
import wave
import io
import struct

# this is how the pitch should change, positive integers increase the frequency, negative integers decrease it.
n = 3
CHUNK = 2048
FORMAT = pyaudio.paFloat32
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                   channels=2,
                   rate=44100,
                   input=True,
                   input_device_index=1,
                   output=True,
                   output_device_index=6,
                   frames_per_buffer=CHUNK)


print("* Started")

def l_effect(d) -> np.ndarray:
    data = np.frombuffer(d, np.int16)
    # data = data * (5000 / 100.)

    l_shift = -14
    r_shift = 14
    
    left, right = data[0::2], data[1::2]
    lf, rf = np.fft.rfft(left), np.fft.rfft(right)
    lf, rf = np.roll(lf, l_shift), np.roll(rf, r_shift)
    lf[l_shift:0], rf[0:r_shift] = 0, 0
    nl, nr = np.fft.irfft(lf), np.fft.irfft(rf)
    ns = np.column_stack((nl, nr)).ravel().astype(np.int16)
    
    return ns.astype(np.int16).tobytes()

def total_disaster(d) -> np.ndarray:
    data = np.frombuffer(d, np.float32)

    freq = np.fft.rfft(data)

    return freq.astype(np.float32).tobytes()

while stream.is_active():
    try:
        input_r = stream.read(CHUNK,  exception_on_overflow = False)

        data = l_effect(input_r)
        # y = np.frombuffer(input_r, np.float32)

        stream.write(data)
    except Exception as e:
        print(e)
        print("* Done")
        stream.stop_stream()

stream.close()
p.terminate()