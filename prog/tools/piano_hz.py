# coding:utf-8
# ピアノの音を周波数として割り出す

import numpy as np

# 適当にa5まであれば20000[Hz]まで足りる

class piano():
  def __init__(self, calc_max_freq=4187):
    # 4186.009[Hz]がピアノの一番高い音
    self.calc_max_freq = calc_max_freq # 計算する最大周波数
    self.hi = np.power(2, 1.0/12.0)  # 音階一つあたりn倍になるか
    self.freq = []
    self.hfreq = []

    # 先に計算しておく
    self.calc_hz()
    self.create_half_list()

    # 扱う最大と最小の周波数
    self.min_f = self.freq[0][0]
    self.max_f = self.freq[-1][-1]

    self.octa_mark = ["A0", "A1", "A2", " A", " a", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9"]
    self.onkai = ["ラ　　", "ラ＃　", "シ　　", "ド　　", "ド＃　", \
        "レ　　", "レ＃　", "ミ　　", "ファ　", "ファ＃", "ソ　　", "ソ＃　", ]

  def __str__(self):
    return str(self.freq)

  # ピアノの音階の周波数を計算
  def calc_hz(self):
    tmp = 27.50 # ピアノの左端の鍵盤

    flg = True
    while flg == True:
      octave = []
      for j in range(1, 13):
        octave.append(tmp)
        tmp *= self.hi
        if self.calc_max_freq < tmp:
          flg = False
          break
      self.freq.append(octave)

  # 音階の中間を計算
  def create_half_list(self):
    freq_list = []
    for i in self.freq:
      for j in i:
        freq_list.append(j)

    # 平均をとる
    for cnt in range(0,len(freq_list)):
      freq_list[cnt] = (freq_list[cnt] + freq_list[cnt+1]) / 2.0
      if cnt == len(freq_list)-2:
        # 一番上は正しくないけどいいや。
        break

    # 2次元配列に変換
    cnt = 1
    octave = []
    for f in freq_list:
      if cnt < 12:
        octave.append(f)
        cnt += 1
      else:
        octave.append(f)
        self.hfreq.append(octave)
        octave = []
        cnt = 1

    self.hfreq.append(octave)

  def print_data(self, data):
    # 周波数
    if data == "freq":
      for oc, i in zip( self.octa_mark, self.freq):
        print('-'*8+oc+'-'*8)
        for on,j in zip( self.onkai, i):
          print(on+"%.3f" % (j))

    # 周波数の中間
    elif data == "hfreq":
      for oc, i in zip( self.octa_mark, self.hfreq):
        print('-'*8+oc+'-'*8)
        for on,j in zip( self.onkai, i):
          print(on+"%.3f" % (j))
    else:
      print("error argument word")

  # 周波数を渡すと、それに近い音を返してくれる
  def hz_to_scale(self, freq):
    if freq < self.min_f:
      # 低周波数側の範囲外は一番低い音を返す
      # (やっているとキリが無いので) どうせ2[Hz]とか再生できないし。。。
      return (0,0)

    if freq > self.max_f:
      # 範囲外の入力は-1を返す
      return -1

    oc = 0
    on = 0
    for i in self.hfreq:
      on = 0
      for j in i:
        if j > float(freq):
          return (oc, on)
          break
        on += 1
      oc += 1

    # 本来存在すればここのreturnにはこないはず
    return -1

  def n_to_octa(self, octa):
    return octa_mark[octa]  # str

  def n_to_onkai(self, data_onkai):
    return onkai[data_onkai]  # str

if __name__ == "__main__":
  my_piano = piano()

  # my_piano.print_data("hfreq")

  while 1:
    hz = float(raw_input("Hz: "))
    oto = my_piano.hz_to_scale(hz)
    if oto == -1:
      print("error")
    else:
      print("%f [Hz] : %d, %d" % (hz, oto[0], oto[1]))
