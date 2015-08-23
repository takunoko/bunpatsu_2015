# coding:utf-8
# 録音と再生の最低限の機能
# 録音したものをwaveに出力して、waveの出力を読み込み再生
# どうやら、普通に再生できてるっぽい。
import pyaudio
import wave
import time

FILE_NAME = 'test.wav'

wf = wave.open(FILE_NAME, 'w')
wf.setsampwidth(1)
wf.setframerate(44100)
wf.setnchannels(1)

p = pyaudio.PyAudio()

input_device_index = 0

# 録音

def callback(in_data, frame_count, time_info, status):
	wf.writeframes(in_data)
	return (None, pyaudio.paContinue)

stream = p.open( format = p.get_format_from_width(wf.getsampwidth()),\
			channels = wf.getnchannels(),\
			rate = wf.getframerate(),\
			input_device_index = input_device_index,\
			input = True,\
			stream_callback = callback)

print(' REC start')
stream.start_stream()

for i in range(5):
	print(str(i) + "[sec]")
	time.sleep(1)

stream.stop_stream()
stream.close()

wf.close()
p.terminate()


# 再生

wf = wave.open( FILE_NAME, 'rb')

p = pyaudio.PyAudio()

def callback( in_data, frame_count, time_info, status ):
	data = wf.readframes(frame_count)
	return (data, pyaudio.paContinue)

stream = p.open( format=p.get_format_from_width(wf.getsampwidth()),\
				channels = wf.getnchannels(),\
				rate = wf.getframerate(),\
				output=True,\
				stream_callback=callback )

print(' Play start')
stream.start_stream()

while( stream.is_active() ):
	time.sleep(0.1)

stream.stop_stream()
stream.close()
wf.close()

p.terminate()
