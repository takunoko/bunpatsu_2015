# coding: utf-8
# waveファイルを読み込み、fftをする

import wave
import sys
import pyaudio

class WaveData:
	def __init__(self, filename):
		self.fname = filename
		print("waveデータの読み込み")
		try:
			self.wavedata = wave.open(self.fname)
			print("成功")
		except:
			print("失敗")

	def __exit__(self, type, value, traceback):
		self.wavedata.close()

	def __str__(self):
		return 'FILE : "'+self.fname+'"'

	def print_data(self):
		print("-"*5+"waveファイルの情報"+"-"*5)
		print("チャンネル数        : ",self.wavedata.getnchannels())
		print("サンプル幅          : ",self.wavedata.getsampwidth())
		print("サンプリング周波数  : ",self.wavedata.getframerate())
		print("フレーム数          : ",self.wavedata.getnframes())
		print("パラメータ          : ",self.wavedata.getparams())
		print("長さ(秒)            : ",float(self.wavedata.getnframes()) / self.wavedata.getframerate())

	def play(self):
		# ストリームの作成
		p = pyaudio.PyAudio()
		stream = p.open(
				format=p.get_format_from_width(self.wavedata.getsampwidth()),
				channels=self.wavedata.getnchannels(),
				rate=self.wavedata.getframerate(),
				output=True)

		# チャンク単位でストリームに音声を出力
		chunk = 1024
		data = self.wavedata.readframes(chunk)
		while data != '':
			stream.write(data)
			data = self.wavedata.readframes(chunk)

		# 使ったものを解放
		stream.close()
		p.terminate()

if __name__ == "__main__":
	argvs = sys.argv
	argc = len(argvs)

	if argc != 2:
		print("format error")
		print("$ python wave_fft.py FILENAME.wave")
		sys.exit()

	sound =  WaveData(argvs[1])
	print(sound)
	sound.print_data()
	sound.play()
