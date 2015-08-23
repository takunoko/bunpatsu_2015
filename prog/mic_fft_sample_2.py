# coding: utf-8
# 参考URL: https://gist.github.com/nobonobo/5237011

import sys
import os
import atexit
import time

import numpy as np
import pyaudio


class Spectrum(object):

    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 16000

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.last_samples = None
        atexit.register(self.pa.terminate)

    # samplesは波形データの文字列
    def fft(self, samples):
        # 窓関数をハニング窓で作成
        win = np.hanning(len(samples))
        # win*samplesでハニング窓関数を適応してる。
        # fft.fft で高速フーリエ変換
        # fftした結果の配列を中央に0がくるようにシフト
        res = np.fft.fftshift(np.fft.fft(win*samples))
        freq = np.fft.fftfreq(len(samples), d=self.RATE**-1)
        # return zip(freq, 20*np.log10(np.abs(res)))
        # np.absは使われてない気がするので削除
        return zip(freq, 20*np.log10(res))

    def callback(self, in_data, frame_count, time_info, status):
        # 波形データを文字列から数値に変換
        data = np.fromstring(in_data, np.float32)
        pr = []
        for f,v in self.fft(data)[256-64:256]:
            pr.append(str(min(9, max(0, int((v+50)/10)))))
        print ''.join(pr)

        return (in_data, self.recording)

    def record(self):
        self.recording = pyaudio.paContinue
        stream = self.pa.open(format = self.FORMAT,
                        channels = self.CHANNELS,
                        rate = self.RATE,
                        input = True,
                        output = False,
                        #frames_per_buffer = self.FRAME_LEN,
                        frames_per_buffer = 512,
                        stream_callback = self.callback)
        stream.start_stream()

        while stream.is_active():
            try:
                # Ctrl+Cを押してから反映されるまでのラグ。適当で良さげ
                time.sleep(1)
            except KeyboardInterrupt:
                self.recording = pyaudio.paAbort

        # stream.start_stream()
        stream.close()

if __name__ == '__main__':
    spe = Spectrum()
    spe.record()
