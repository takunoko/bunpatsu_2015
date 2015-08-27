# -*- coding: utf-8 -*-
# サンプルソース : http://yukara-13.hatenablog.com/entry/2013/12/05/025655
# 自分の環境ではalsaaudioの代わりにpyaudioを利用
import pyaudio  # alsaaudioの代わりにpyaudioを使う
from scipy import arange, fromstring, roll, zeros
import numpy as np

# 描画関連
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

import sys
sys.path.append('./tools/')  # モジュールの場所を追加
from piano_hz import piano
from dtmf import DTMF
from play_wave import PLAY_WAVE

# 音声出力フィアルの保存名
OUTPUT_FILE_NAME = 'sample_01'

# 配列の1~12(ド~シ)に対応する電話の数字
# 適当に ド='1' シ='*'
phone_scale = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '#', '0', '*']

# 生成する音の大きさ 最大値は1.0
DTMF_AMPLITUDE = 1.0

# fftLen = 2048
# fftLen = 1000
# fftLen = 4096  # 10[Hz]刻み
fftLen = 8192  # 5[Hz]刻み
# fftLen = 16384 # 2.7[Hz]刻み

# shift = 512
# shift = 1024
shift = 2048
# shift = 4096

signal_scale = 1. / 2000

capture_setting = {
    'ch': 1,
    # 'fs' : 16000,
    'fs': 44100,
    'chunk': shift,
    'format': pyaudio.paInt16
}


def my_fft(samples):
    # 窓関数をハニング窓で作成
    win = np.hanning(len(samples))
    # win*samplesでハニング窓関数を適応してる
    res = np.fft.fft(win*samples)  # resは虚数となる

    # db単位
    # return 20*np.log10(np.abs(res)) #db単位に直すと、ノイズを大量に拾ってしまうのでパス
    return res


class C_spectrumAnalyzer():
    def __init__(self):
        # いろいろ設定関連
        self.ch = capture_setting['ch']
        self.fs = capture_setting['fs']
        self.chunk = capture_setting['chunk']
        self.data_format = capture_setting['format']

        # マイクの利用
        self.p = pyaudio.PyAudio()
        self.apiCnt = self.p.get_host_api_count()

        # どのマイクが利用可能か?
        # print('Host API Count: %d' % apiCnt)
        # for cnt in range(apiCnt):
        # 	print(p.get_host_api_info_by_index(cnt))

        # input_deveice_index = 1 # マイクの選択(どうせ1しか使えない...)

        self.stream = self.p.open(
            format=self.data_format,
            channels=self.ch,
            rate=self.fs,
            input=True,
            frames_per_buffer=self.chunk)

        # fftした際の配列のn番目の周波数を配列として取得
        fft_freq = np.fft.fftfreq(fftLen, d=self.fs**-1)

        # =========================
        # ピアノとfft結果の対応作成
        # =========================

        # my_piano = piano(30000)  # 考慮する最大周波数
        self.my_piano = piano(self.fs/1.5)

        self.freq_list = []
        for li, freq in enumerate(fft_freq):
            tmp_freq_data = []
            # tmp_freq_data['freq'] = freq
            tmp_freq_data.append(freq)

            conv_freq = self.my_piano.hz_to_scale(freq)
            if conv_freq == -1:
                print('error higher freq: %f' % (freq))
                print('pianoを宣言するときに、もっと高い周波数まで考慮するように宣言しよう!')
                sys.exit(-1)
            else:
                # tmp_freq_data['Scale'] = conv_freq[0]
                # tmp_freq_data['doremi'] = conv_freq[1]
                tmp_freq_data.append(conv_freq[0])
                tmp_freq_data.append(conv_freq[1])

            self.freq_list.append(tmp_freq_data)

        # =========================
        #   DTMFのサンプルを作成
        # =========================
        self.my_dtmf = DTMF()
        # それぞれの音(1~9,#,0,*)に対応するサンプルwave
        self.wave_list = {}
        for num in range(0, 10):
            self.wave_list[str(num)] = self.my_dtmf.create_dtmf(
                DTMF_AMPLITUDE, str(num), self.chunk / (self.fs*1.3))
        self.wave_list['#'] = self.my_dtmf.create_dtmf(
            DTMF_AMPLITUDE, '#', self.chunk / (self.fs*1.0))
        self.wave_list['*'] = self.my_dtmf.create_dtmf(
            DTMF_AMPLITUDE, '*', self.chunk / (self.fs*1.0))
        # 音を鳴らさない = 0[Hz]の音を生成しておく
        self.wave_list['N'] = self.my_dtmf.createSineWave(
            DTMF_AMPLITUDE, 0, 0, 8000.0, self.chunk / float(self.fs))

    def setup_windo(self):
        # アプリケーション作成
        self.app = QtGui.QApplication([])
        self.app.quitOnLastWindowClosed()
        # メインウィンドウ
        self.mainWindow = QtGui.QMainWindow()
        self.mainWindow.setWindowTitle('Spectrum Analyzer')  # Title
        self.mainWindow.resize(800, 300)  # Size
        # キャンパス
        centralWid = QtGui.QWidget()
        self.mainWindow.setCentralWidget(centralWid)
        # レイアウト
        lay = QtGui.QVBoxLayout()
        centralWid.setLayout(lay)
        # スペクトル表示用ウィジット
        specWid = pg.PlotWidget(name='spectrum')
        self.specItem = specWid.getPlotItem()
        self.specItem.setMouseEnabled(y=False)  # y軸方向に動かせなくする
        self.specItem.setYRange(0, 1000)
        self.specItem.setXRange(0, fftLen / 4, padding=0)  # デフォで表示する幅をいじれる
        # Axis
        # X軸についてのいろいろプロット?
        specAxis = self.specItem.getAxis('bottom')
        specAxis.setLabel('Frequency [Hz]')
        specAxis.setScale(self.fs / 2. / (fftLen / 2 + 1))
        hz_interval = 1000
        # 配列のn番目と表示する周波数の対応
        newXAxis = (arange(int(self.fs / 2 / hz_interval)) + 1) * hz_interval
        oriXAxis = newXAxis / (self.fs / 2. / (fftLen / 2 + 1))
        specAxis.setTicks([zip(oriXAxis, newXAxis)])

        # キャンパスにのせる
        lay.addWidget(specWid)

        # ウィンドウ表示
        self.mainWindow.show()

    # data: 保存データ(ドレミのデータ), distance: 一つの音のデータ, file_name: ファイル名
    def save_score_data(self , score_data, distance, file_name):
        import csv
        old_data = ''
        wave_data = ''

        writecsv = csv.writer(file(file_name+'.csv', 'w'), lineterminator='\n')

        print('DTMF音楽作成中...')
        cnt = 0
        for data in score_data:
            if old_data == data:
                cnt += 1
            else:
                data_time = distance*cnt
                print('%s, %f[s]' % (data, data_time))
                # 波形を生成
                wave_data += self.my_dtmf.create_dtmf( DTMF_AMPLITUDE, data, data_time)
                writecsv.writerow([data,data_time])
                cnt = 1
            old_data = data

        self.my_dtmf.save(wave_data, 8000, 16, file_name+'.wav')
        print('DTMFに変換したものを %s として保存しました。' % (file_name+'.wav'))

    def spectrumAnalyzer(self):

        # FFT する信号の初期化
        signal = zeros(fftLen, dtype=float)

        # Update
        print('音声入力ループ')

        sound_data = []
        # 適当に5秒間実行して終了
        for n in xrange(0, self.fs * 10 / self.chunk):
            try:
                # dataは文字列型
                data = self.stream.read(self.chunk)
            except IOError as ex:
                # よくわからんけど、しばらく実行していると結構な頻度でミスってる
                if ex[1] != pyaudio.paInputOverflowed:
                    raise
                data = '\x00' * self.chunk
                print('errorrrrrrrrrrrrrrrrrr')

            num_data = fromstring(data, dtype='int16')
            signal = roll(signal, - self.chunk)
            signal[- len(num_data):] = num_data
            fftspec = my_fft(signal)

            spec = abs(fftspec[1: fftLen / 2 + 1]) * signal_scale  # スペクトル
            # print('Max : %.5f' % freq_list[np.argmax(spec)])

            if max(spec) >= 200 and np.argmax(spec) > 3:
                print('spec: %s' % str(max(spec)))
                max_list_num = np.argmax(spec)
                print('Max : %8.3f , %s, %s' % (
                    self.freq_list[max_list_num][0],
                    self.my_piano.octa_mark[self.freq_list[max_list_num][1]],
                    self.my_piano.onkai[self.freq_list[max_list_num][2]])
                )
                sound_data.append(phone_scale[self.freq_list[max_list_num][2]])
            else:
                print('none')
                sound_data.append('N')

            self.specItem.plot(spec, clear=True)
            QtGui.QApplication.processEvents()

        self.save_score_data(sound_data, self.chunk/float(self.fs), OUTPUT_FILE_NAME)

        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    speana = C_spectrumAnalyzer()
    speana.setup_windo()
    speana.spectrumAnalyzer()

    w_player = PLAY_WAVE()
    w_player.play(OUTPUT_FILE_NAME+'.wav')
