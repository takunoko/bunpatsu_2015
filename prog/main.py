# -*- coding: utf-8 -*-
# サンプルソース : http://yukara-13.hatenablog.com/entry/2013/12/05/025655
# 自分の環境ではalsaaudioの代わりにpyaudioを利用

import pyaudio # alsaaudioの代わりにpyaudioを使う
from scipy import arange, fromstring, roll, zeros
import numpy as np

# 描画関連
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import csv
import sys
sys.path.append("./tools/")  # モジュールの場所を追加
from piano_hz import piano

# fftLen = 2048
# fftLen = 1000
# fftLen = 4096  # 10[Hz]刻み
fftLen = 8192  # 5[Hz]刻み
# fftLen = 16384 # 2.7[Hz]刻み

# shift = 512
# shift = 1024
shift = 2048

signal_scale = 1. / 2000

capture_setting = {
    "ch" : 1,
    # "fs" : 16000,
    "fs" : 44100,
    "chunk" : shift,
    "format" : pyaudio.paInt16
}

def my_fft( samples):
    # 窓関数をハニング窓で作成
    win = np.hanning(len(samples))
    # win*samplesでハニング窓関数を適応してる。
    res = np.fft.fft(win*samples) # resは虚数となる

		# フーリエ変換した際のx座標の周波数を求める
    # freq = np.fft.fftfreq(len(samples), d=capture_setting["self.chunk"]**-1)

    # db単位
    # return 20*np.log10(np.abs(res)) #db単位に直すと、ノイズを大量に拾ってしまうのでパス
    return res

class C_spectrumAnalyzer():
  def __init__(self):
    # いろいろ設定関連
    self.ch = capture_setting["ch"]
    self.fs = capture_setting["fs"]
    self.chunk = capture_setting["chunk"]
    self.data_format = capture_setting["format"]

    # マイクの利用
    p = pyaudio.PyAudio()
    self.apiCnt = p.get_host_api_count()

    # どのマイクが利用可能か?
    # print("Host API Count: %d" % apiCnt)
    # for cnt in range(apiCnt):
    # 	print(p.get_host_api_info_by_index(cnt))

    input_deveice_index = 1 # マイクの選択(どうせ1しか使えない...)

    self.stream = p.open(
                format = self.data_format,
                channels = self.ch,
                rate = self.fs,
                input = True,
                frames_per_buffer = self.chunk)

    fft_freq = np.fft.fftfreq( fftLen, d=self.fs**-1)

    # my_piano = piano(30000)  # 考慮する最大周波数
    self.my_piano = piano(self.fs/1.5)  # 考慮する最大周波数

    self.freq_list = []
    # tmp_freq_data = {}
    for i,freq in enumerate(fft_freq):
      tmp_freq_data = []
      # tmp_freq_data["freq"] = freq
      tmp_freq_data.append(freq)

      conv_freq = self.my_piano.hz_to_scale(freq)
      if conv_freq == -1:
        print("error higher freq: %f" % (freq))
        print("pianoを宣言するときに、もっと高い周波数まで考慮するように宣言しよう!")
        sys.exit(-1)
      else:
      # tmp_freq_data["Scale"] = conv_freq[0]
      # tmp_freq_data["doremi"] = conv_freq[1]
        tmp_freq_data.append(conv_freq[0])
        tmp_freq_data.append(conv_freq[1])

      self.freq_list.append(tmp_freq_data)

    # どうやらリストはあってそう。
    # for i, freq in enumerate(self.freq_list):
    #   print("[%5d]  %8.3f | %d | %d " % (i, self.freq_list[i][0], self.freq_list[i][1], self.freq_list[i][2]))

    # np.savetxt("freq_list.txt", self.freq_list)


  def setup_windo(self):
    # ========
    #  Layout
    # ========

    ### アプリケーション作成
    self.app = QtGui.QApplication([])
    self.app.quitOnLastWindowClosed()

    ### メインウィンドウ
    self.mainWindow = QtGui.QMainWindow()
    self.mainWindow.setWindowTitle("Spectrum Analyzer") # Title
    self.mainWindow.resize(800, 300) # Size

    ### キャンパス
    centralWid = QtGui.QWidget()
    self.mainWindow.setCentralWidget(centralWid)

    ### レイアウト！！
    lay = QtGui.QVBoxLayout()
    centralWid.setLayout(lay)

    ### スペクトル表示用ウィジット
    specWid = pg.PlotWidget(name="spectrum")
    self.specItem = specWid.getPlotItem()
    self.specItem.setMouseEnabled(y = False) # y軸方向に動かせなくする
    self.specItem.setYRange(0, 1000)
    self.specItem.setXRange(0, fftLen / 4, padding = 0) # デフォで表示する幅をいじれる

    ### Axis
    # X軸についてのいろいろプロット?
    specAxis = self.specItem.getAxis("bottom")
    specAxis.setLabel("Frequency [Hz]")
    specAxis.setScale(self.fs / 2. / (fftLen / 2 + 1))
    hz_interval = 1000
    # たぶん、この部分が適当
    newXAxis = (arange(int(self.fs / 2 / hz_interval)) + 1) * hz_interval
    oriXAxis = newXAxis / (self.fs / 2. / (fftLen / 2 + 1))
    specAxis.setTicks([zip(oriXAxis, newXAxis)])

    ### キャンパスにのせる
    lay.addWidget(specWid)

    ### ウィンドウ表示
    self.mainWindow.show()

  def spectrumAnalyzer(self):
    ### FFT する信号の初期化
    signal = zeros(fftLen, dtype = float)

    freq_list = np.fft.fftfreq( fftLen, d=self.fs**-1)

    ### Update
    print("音声入力ループ")
    while 1:
      try:
        data = self.stream.read(self.chunk)
        # print("ok")
      except IOError as ex:
        # よくわからんけど、しばらく実行していると結構な頻度でミスってる
        if ex[1] != pyaudio.paInputOverflowed:
          raise
        data = '\x00' * self.chunk
        print("error")

      num_data = fromstring(data, dtype = "int16")
      signal = roll(signal, - self.chunk)
      signal[- len(num_data) :] = num_data
      fftspec = my_fft( signal)

      spec = abs(fftspec[1 : fftLen / 2 + 1]) * signal_scale # スペクトル
      # print("Max : %.5f" % freq_list[np.argmax(spec)])

      if max(spec) >= 200:
        print("Max : %8.3f , %s, %s" % ( \
          self.freq_list[np.argmax(spec)][0], \
          self.my_piano.octa_mark[self.freq_list[np.argmax(spec)][1]], \
          self.my_piano.onkai[self.freq_list[np.argmax(spec)][2]]) \
          # self.freq_list[np.argmax(spec)][1], \
          # self.freq_list[np.argmax(spec)][2]) \
        )

      self.specItem.plot( spec, clear = True)
      # specItem.plot( fftspec, clear = True)
      QtGui.QApplication.processEvents()

if __name__ == "__main__":
  speana = C_spectrumAnalyzer()
  speana.setup_windo()
  speana.spectrumAnalyzer()

