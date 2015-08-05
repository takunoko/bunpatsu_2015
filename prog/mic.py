# coding: utf-8
import pyaudio
import wave

CHUNK = 1024
# CHUNK = 100
FORMAT = pyaudio.paInt16
CHANNELS = 1 # 入力のチャンネル数に合わせて変更する必要がある。イヤホン付属は1
RATE = 44100

RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

# PCに接続されているオーディオデバイスの情報を表示
apiCnt = p.get_host_api_count()
print("Host API Count: %d" % apiCnt)
for cnt in range(apiCnt):
	print(p.get_host_api_info_by_index(cnt))

# 入力デバイスの指定
# なんだかWebカメはうまく認識してないみたい
input_deveice_index = 1

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

# 音声フレームのリスト
frames = []

# ループの回数だけ計算て繰り返してる
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	# ストリームからchunk分のデータが溜まったら持ってくる感じ?
 data = stream.read(CHUNK)
 frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

# 出力結果の書き込み
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# この辺で書き込むwaveの設定
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
# 実際の書き込み
wf.writeframes(b''.join(frames))
wf.close()
