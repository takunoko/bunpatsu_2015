# coding:utf-8
import pyaudio  # alsaaudioの代わりにpyaudioを使う
# import numpy as np
import csv

import sys
sys.path.append('./tools/')  # モジュールの場所を追加
from dtmf import DTMF
from play_wave import PLAY_WAVE


# 配列の1~12(ド~シ)に対応する電話の数字
# 適当に ド='1' シ='*'
phone_scale = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '#', '0', '*']

# 音声出力フィアルの保存名
FILE_NAME = 'sample_01'

# 生成する音の大きさ 最大値は1.0
DTMF_AMPLITUDE = 1.0


class csv_dtmf():
    def __init__(self):
        self.my_dtmf = DTMF()

    def read_scale(self, file_name):  # 譜面データを読み込み、配列にして返す
        scale_data = []
        csv_reader = csv.reader(open(file_name+'.csv', 'rb'), delimiter=',', quotechar=',')
        for row in csv_reader:
            scale_data.append(row)

        return scale_data

    def create_dtmf(self, data):
        wave_data = ''
        for d in data:
            wave_data += self.my_dtmf.create_dtmf(DTMF_AMPLITUDE, d[0], float(d[1]))

        return wave_data

    def save_wave(self, wave_data, file_name):
        self.my_dtmf.save(wave_data, 8000, 16, file_name)


if __name__ == '__main__':
    decorder = csv_dtmf()
    player = PLAY_WAVE()
    scale_data = decorder.read_scale(FILE_NAME)
    wave_data = decorder.create_dtmf(scale_data)
    decorder.save_wave(wave_data, FILE_NAME+'.wav')
    player.play(FILE_NAME+'.wav')
