# coding: utf-8
# 参考URL: https://gist.github.com/nobonobo/5237011

import atexit
import time

import numpy as np
import pyaudio

import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Spectrum(object):

    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    # ピアノを基準に考えたときに最大でも3500[Hz]ちょいだから、8000[Hz]まであれば問題ない?
    # RATE = 16000
    RATE = 44100
    # WINDOW_SIZE = 1024
    # WINDOW_SIZE = 4410
    WINDOW_SIZE = 1102  # 4410の1/4ぐらい
    # fftした結果の解像度?も変わってくる。大きい方が解像度が高いけど、時間的細かさに欠けてしまう。

    cnt = 0

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.last_samples = None
        atexit.register(self.pa.terminate)
        # 出力波形の保存用
        self.wave_data = []
        self.f = np.fft.fftfreq(self.WINDOW_SIZE, d=self.RATE**-1)[0:self.WINDOW_SIZE/2]

    # samplesは波形データの文字列
    def fft(self, samples):
        # 窓関数をハニング窓で作成
        win = np.hanning(len(samples))
        # win*samplesでハニング窓関数を適応してる。
        # fftした結果の配列を中央に0がくるようにシフト
        # res = np.fft.fftshift(np.fft.fft(win*samples)) # shiftすると、描画波形がおかしくなる。

        # fft.fft で高速フーリエ変換
        res = np.fft.fft(win*samples)
				# フーリエ変換した際のx座標の周波数を求める
        freq = np.fft.fftfreq(len(samples), d=self.RATE**-1)

        self.cnt += 1
        # # return zip(freq, 20*np.log10(np.abs(res)))
        # # np.absは使われてない気がするので削除
        # 微妙なので、absを残した。。。

        # print("freq : ")
        # print(freq[256-64:256])
        # print(freq[0:int(self.WINDOW_SIZE/2)])
        return zip(freq, 20*np.log10(np.abs(res)))

    def callback(self, in_data, frame_count, time_info, status):
        # 波形データを文字列から数値に変換
        data = np.fromstring(in_data, np.float32)
        pr = []
        pr_int_list = []
        for f,v in self.fft(data)[0:(self.WINDOW_SIZE/2)]:
            pr.append(str(min(9, max(0, int((v+50)/10)))))
            pr_int_list.append((v+50))
            self.wave_freq = f
        print ''.join(pr)

        # 後から波形を描画するためのデータを保存
        self.wave_data.append(pr_int_list)

        return (in_data, self.recording)

    def record(self):
        self.recording = pyaudio.paContinue
        stream = self.pa.open(format = self.FORMAT,
                        channels = self.CHANNELS,
                        rate = self.RATE,
                        input = True,
                        output = False,
                        #frames_per_buffer = self.FRAME_LEN,
                        frames_per_buffer = self.WINDOW_SIZE,
                        stream_callback = self.callback)

        stream.start_stream()

        while stream.is_active():
            try:
                # ctrl+cを押してから反映されるまでのラグ。適当で良さげ
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.recording = pyaudio.paAbort

        stream.close()

    def disp_wave(self):
        fig = plt.figure()
        frame_list = []
        for i,w in enumerate(self.wave_data):
            # plt.xlim( 0, 3000)
            plt.xlim( 0, 22050)
            plt.ylim( 0, 100)
            one_fram = plt.plot( self.f, w, "g-")
            frame_list.append(one_fram)

        ani = animation.ArtistAnimation( fig, frame_list, interval = 100, repeat_delay = 10)
        plt.show()

if __name__ == '__main__':
    spe = Spectrum()
    print("recording start")
    spe.record()
    print("disp wave")
    spe.disp_wave()
