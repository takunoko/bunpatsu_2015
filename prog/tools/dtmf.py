# coding: utf-8
# 電話のピッポッパッって音を鳴らしてみる。

import wave
import struct
import numpy as np
import pylab


class DTMF():
    # def __init__(self):
    #   print("init")

    def save(self, data, fs, bit, filename):
        # WAVEファイルへ出力
        wf = wave.open(filename, "w")
        wf.setnchannels(1)
        wf.setsampwidth(bit / 8)
        wf.setframerate(fs)
        wf.writeframes(data)
        wf.close()

    def createSineWave(self, A, f0, f1, fs, length):
        """振幅A、基本周波数f0、サンプリング周波数 fs、
        長さlength秒の正弦波を作成して返す"""
        data = []
        # [-1.0, 1.0]の小数値が入った波を作成
        for n in pylab.arange(length * fs):  # nはサンプルインデックス
            wave = np.sin(2 * np.pi * f0 * n / fs) + np.sin(2 * np.pi * f1 * n / fs)
            s = A/2 * wave
            # 振幅が大きい時はクリッピング
            if s > 1.0:
                s = 1.0
            if s < -1.0:
                s = -1.0
            data.append(s)
        # [-32768, 32767]の整数値に変換
        data = [int(x * 32767.0) for x in data]
        # バイナリに変換
        data = struct.pack("h" * len(data), *data)  # listに*をつけると引数展開される
        return data

    def play(self, data, fs, bit):
        import pyaudio
        # ストリームを開く
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=int(fs),
                        output=True
                        )

        print(' Play start')

        # チャンク単位でストリームに出力し音声を再生
        chunk = 1024
        sp = 0  # 再生位置ポインタ
        buffer = data[sp:sp+chunk]
        while buffer != '':
            stream.write(buffer)
            sp = sp + chunk
            buffer = data[sp:sp+chunk]

        stream.close()
        p.terminate()

    # 数値に対応したdtmfの周波数ペアを返す
    # 引数は、文字を受け取る
    # A,B,C,Dには未対応
    def dtmf_freq(self, number):
        freq_row = (697, 770, 852, 941)
        freq_col = (1209, 1336, 1477, 1633)

        if(number == '0'):
            row = 3
            col = 1
        elif(number == '#'):
            row = 3
            col = 2
        elif(number == '*'):
            row = 3
            col = 0
        elif(number == 'N'): # 周波数0(音が出ない)を作成する
            return ( 0, 0)
        else:
            num = int(number)-1
            row = int(num / 3)
            col = int(num % 3)

        return (freq_row[row], freq_col[col])

    # 数字と時間の入力で音を生成する
    def create_dtmf(self, amp, number, length):
        freq = self.dtmf_freq(number)
        data = self.createSineWave(amp, freq[0], freq[1], 8000.0, length)
        return data

if __name__ == "__main__":
    my_dtmf = DTMF()

    number = raw_input("number or * or # :")
    # number = "111111111111111111111"
    # number = "1" * 3
    numberList = list(number)

    allData = ""
    for num in numberList:
        freq = my_dtmf.dtmf_freq(num)
        # data = my_dtmf.createSineWave(1.0, freq[0], freq[1], 8000.0, 0.046)
        data = my_dtmf.createSineWave(1.0, freq[0], freq[1], 8000.0, 0.8)
        # data = my_dtmf.createSineWave(1.0, 40, 0, 8000.0, 1.0)
        print("%c %d[Hz]+%d[Hz]" % (str(num), freq[0], freq[1]))
        # my_dtmf.play(data, 8000, 16)
        allData += data
    my_dtmf.save(allData, 8000, 16, str(number)+".wav")
