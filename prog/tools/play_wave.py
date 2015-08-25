# coding:utf-8
# 引数のwaveファイルをとりあえす再生する
import pyaudio
import wave
import time
import sys


class PLAY_WAVE():
    def __init__(self):
        self.p = pyaudio.PyAudio()

    def callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    def play(self, file_name):
        self.wf = wave.open(file_name, 'rb')
        stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True,
            stream_callback=self.callback)

        stream.start_stream()

        while(stream.is_active()):
            time.sleep(0.1)

        stream.stop_stream()
        stream.close()
        self.wf.close()

        self.p.terminate()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("command error")
        print("$ python %s FILE_NAME" % sys.argv[0])
        sys.exit(-1)

    player = PLAY_WAVE()
    player.play(sys.argv[1])
