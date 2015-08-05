# coding: utf-8
import pyaudio
import wave

from numpy import frombuffer as fb
from pylab import plot,show

# CHUNK = 1024
CHUNK = 100
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
# RATE = 16000

RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

# オーディオデバイスの情報を表示
apiCnt = p.get_host_api_count()
print("Host API Count: %d" % apiCnt)
for cnt in range(apiCnt):
	print(p.get_host_api_info_by_index(cnt))

input_deveice_index = 1

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []
inp = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
 data = stream.read(CHUNK)
 frames.append(data)
 inp.extend(fb(data,dtype = "int16")) # ただの型変換らしい

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

plot(inp)
show()
