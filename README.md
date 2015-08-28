# Music -> DTMF

### 製作 : たくのこ

# 概要
マイクに入力された音を電話の「ピッ・ポッ・パッ」に自動的に対応させます。

## プログラムの実行方法
プログラム実行までの流れ。
### 初回設定
```shell
cd $HOME/Develop/5/bunpatu2015/prog/
pyenv shell anaconda-2.1.0
```
![初回設定](https://raw.githubusercontent.com/takunoko/music_dtmf/master/README_files/setting.png "実行コマンド")

### 実行コマンド
```shell
python main.py
```
![実行コマンド](https://raw.githubusercontent.com/takunoko/music_dtmf/master/README_files/start.png)

プログラムが開始すると、しばらくしてからスペクトルを表示するウィンドウが立ち上がります。
![スペクトル](https://raw.githubusercontent.com/takunoko/music_dtmf/master/README_files/spec.png)

この状態から約10秒間の録音が始まり、その間にリアルタイムでSTFT(短時間フーリエ変換)を行い入力をスペクトルに変換したものがリアルタイムで表示されます。
また、最も大きい音の周波数に対応する音階を表示します
![変換](https://raw.githubusercontent.com/takunoko/music_dtmf/master/README_files/do.png)


録音終了後、ある一定値以上の入力に対して、対応する音階と時間を求めます。

出力
- 電話のキーとその音のでる長さをcsvファイルに書き出します
- 音階と対応した電話のキーの波形を生成し.wavファイルとして保存。

生成されれた波形からDTMFに変換した譜面を再生します。


# ここから説明 ↓

## はじめに
2015 関東甲信越地方の文化発表会向けの説明内容です。プログラムと関係ないようなことも書いてありますが、あまり気にしないでください…。

それと、結構適当なことを書いてるかもしれないのですが、プログラムできないので勘弁してください><

## 環境
- Mac OS X (Yosemite) 10.10.5
	- MacBook Air Mid2013 / CPU: Intel Core i5 / Mem: 4GB
- Python 2.7.8 [anaconda-2.1.0]
	- anacondaはPythonに数値計算とかいろいろなライブラリがまとまって入ったようなもの
	- pyAudio 0.2.7
		- pythonからマイクやスピーカーを使うためのライブラリ
	- PyQtGraph
		- pyqt(GUIツール)を用いてグラフを描くもの。[公式サイト](http://www.pyqtgraph.org/)
	- numpy
		- pythonで有名な数値計算ライブラリ。多次数値配列に対して高速にいろいろな処理がができたりもろもろ。とても便利。
	- scipy
		- 同じくpythonで有名な数値計算ライブラリ。計算式の微分とかもできる(はず。)

## プログラムの流れ
マイクから音楽を入力 -> 短時間高速フーリエ変換(STFT)により周波数領域に変換 -> ピアノのどの音階に対応するか -> 音階に対応するDTMF音 -> 波形を生成 -> .wavとして保存

だいたいこんな感じです。

## DTMF
詳しくは、[Wikipedia](http://www.wikiwand.com/ja/DTMF)とかを参照してもらえるとわかりやすいです。
ざっくり説明すると、0~9,*,#にそれぞれが2種類のsin波をたし合わせたもので表現されているということです。この音が「ピッポッパッ」と聞こえるわけです





