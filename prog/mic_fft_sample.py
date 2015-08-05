# -*- coding: utf-8 -*-
import sys
# import alsaaudio
import pyaudio # alsaaudioの代わりにpyaudioを使う
from scipy import arange, fft, fromstring, roll, zeros

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

fftLen = 2048
# shift = 100
# shift = 1024
shift = 4096
signal_scale = 1. / 2000

capture_setting = {
    "ch" : 1,
    # "fs" : 16000,
    "fs" : 44100,
    "chunk" : shift,
    "format" : pyaudio.paInt16
}

def spectrumAnalyzer():
    global fftLen, capture_setting, signal_scale
    # ========================
    #  Capture Sound from Mic
    # ========================
    ch = capture_setting["ch"]
    fs = capture_setting["fs"]
    chunk = capture_setting["chunk"]
    ## inPCM = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
    ## inPCM.setchannels(ch)
    ## inPCM.setrate(fs)
    ## inPCM.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    ## inPCM.setperiodsize(chunk)

    p = pyaudio.PyAudio()
    apiCnt = p.get_host_api_count()
    print("Host API Count: %d" % apiCnt)
    for cnt in range(apiCnt):
    	print(p.get_host_api_info_by_index(cnt))

    input_deveice_index = 1
    stream = p.open(format=capture_setting["format"],
                channels=capture_setting["ch"],
                rate=capture_setting["fs"],
                input=True,
                frames_per_buffer=capture_setting["chunk"])

    ### FFT する信号
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
    specItem.setXRange(0, fftLen / 2, padding = 0)
    ### Axis
    specAxis = specItem.getAxis("bottom")
    specAxis.setLabel("Frequency [Hz]")
    specAxis.setScale(fs / 2. / (fftLen / 2 + 1))
    hz_interval = 500
    newXAxis = (arange(int(fs / 2 / hz_interval)) + 1) * hz_interval
    oriXAxis = newXAxis / (fs / 2. / (fftLen / 2 + 1))
    specAxis.setTicks([zip(oriXAxis, newXAxis)])
    ### キャンパスにのせる
    lay.addWidget(specWid)

    ### ウィンドウ表示
    mainWindow.show()

    ### Update
    print("音声入力ループ")
    while 1:
    # for i in xrange(10):
      # i += 1
      # length, data = inPCM.read()
      ## length, data = stream.read(chunk)
      try:
        data = stream.read(chunk)
        # print("ok")
      except IOError as ex:
        if ex[1] != pyaudio.paInputOverflowed:
          raise
        data = '\x00' * chunk
        # print("error")

      ## num_data = fromstring(data, dtype = "int16")
      ## signal = roll(signal, - chunk)
      ## signal[- chunk :] = num_data
      ## fftspec = fft(signal)
      ## specItem.plot(abs(fftspec[1 : fftLen / 2 + 1] * signal_scale), clear = True)
      ## QtGui.QApplication.processEvents()


if __name__ == "__main__":
    spectrumAnalyzer()
