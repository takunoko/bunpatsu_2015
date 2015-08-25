# -*- coding: utf-8 -*-
# サンプルソース : http://yukara-13.hatenablog.com/entry/2013/12/05/025655
# 自分の環境ではalsaaudioの代わりにpyaudioを利用
import sys
import pyaudio # alsaaudioの代わりにpyaudioを使う
from scipy import arange, fromstring, roll, zeros
import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import csv
import sys

# fftLen = 2048
# fftLen = 1000
# fftLen = 4096
# fftLen = 8192
fftLen = 16384

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
    # freq = np.fft.fftfreq(len(samples), d=capture_setting["chunk"]**-1)

    # db単位
    # return 20*np.log10(np.abs(res)) #db単位に直すと、ノイズを大量に拾ってしまうのでパス
    return res

def spectrumAnalyzer():
    global fftLen, capture_setting, signal_scale
    # ========================
    #  Capture Sound from Mic
    # ========================
    ch = capture_setting["ch"]
    fs = capture_setting["fs"]
    chunk = capture_setting["chunk"]

    p = pyaudio.PyAudio()
    apiCnt = p.get_host_api_count()

    # どのマイクが利用可能か?
    # print("Host API Count: %d" % apiCnt)
    # for cnt in range(apiCnt):
    # 	print(p.get_host_api_info_by_index(cnt))

    input_deveice_index = 1 # マイクの選択(どうせ1しか使えない...)

    stream = p.open(
                format=capture_setting["format"],
                channels=capture_setting["ch"],
                rate=capture_setting["fs"],
                input=True,
                frames_per_buffer=capture_setting["chunk"])

    ### FFT する信号の初期化
    signal = zeros(fftLen, dtype = float)

    # ========
    #  Layout
    # ========

    ### アプリケーション作成
    app = QtGui.QApplication([])
    app.quitOnLastWindowClosed()

    ### メインウィンドウ
    mainWindow = QtGui.QMainWindow()
    mainWindow.setWindowTitle("Spectrum Analyzer") # Title
    mainWindow.resize(800, 300) # Size

    ### キャンパス
    centralWid = QtGui.QWidget()
    mainWindow.setCentralWidget(centralWid)

    ### レイアウト！！
    lay = QtGui.QVBoxLayout()
    centralWid.setLayout(lay)

    ### スペクトル表示用ウィジット
    specWid = pg.PlotWidget(name="spectrum")
    specItem = specWid.getPlotItem()
    specItem.setMouseEnabled(y = False) # y軸方向に動かせなくする
    specItem.setYRange(0, 1000)
    specItem.setXRange(0, fftLen / 4, padding = 0) # デフォで表示する幅をいじれる

    ### Axis
    # X軸についてのいろいろプロット?
    specAxis = specItem.getAxis("bottom")
    specAxis.setLabel("Frequency [Hz]")

    specAxis.setScale(fs / 2. / (fftLen / 2 + 1))
    hz_interval = 1000
    # たぶん、この部分が適当
    newXAxis = (arange(int(fs / 2 / hz_interval)) + 1) * hz_interval

    oriXAxis = newXAxis / (fs / 2. / (fftLen / 2 + 1))
    specAxis.setTicks([zip(oriXAxis, newXAxis)])

    ### キャンパスにのせる
    lay.addWidget(specWid)

    ### ウィンドウ表示
    mainWindow.show()

    freq_list = np.fft.fftfreq( fftLen, d=capture_setting["fs"]**-1)
    np.savetxt( "output.txt", freq_list)
    print(type(freq_list))

    print(freq_list[0:len(freq_list)/2])
    print(len(freq_list)/2)

    sys.exit(-1)

    ### Update
    print("音声入力ループ")
    while 1:
      try:
        data = stream.read(chunk)
        # print("ok")
      except IOError as ex:
        # よくわからんけど、しばらく実行していると結構な頻度でミスってる
        if ex[1] != pyaudio.paInputOverflowed:
          raise
        data = '\x00' * chunk
        print("error")

      num_data = fromstring(data, dtype = "int16")
      signal = roll(signal, - chunk)
      # signal[- chunk :] = num_data
      # len(num_data) == chunk == shitf のはず
      signal[- len(num_data) :] = num_data
      fftspec = my_fft( signal)

      spec = abs(fftspec[1 : fftLen / 2 + 1] * signal_scale) # スペクトル
      print("Max : %.5f" % freq_list[np.argmax(spec)])

      specItem.plot( spec, clear = True)
      # specItem.plot( fftspec, clear = True)
      QtGui.QApplication.processEvents()


if __name__ == "__main__":
    spectrumAnalyzer()
