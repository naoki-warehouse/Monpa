# -*- coding: utf-8 -*-
from dsp import encoder #音声変換ライブラリ dsp.py
from matplotlib import pylab as plt #グラフ描画ライブラリ

enc = encoder() #encoderインスタンス作成
num = 0
#音声ファイルの先頭部分に無音部分を追加する。
#本当は必要ない
for i in range(10):
    enc.blank()
    num += 441
print("Blank:"+str(num))
#文字列を読み込む
str = input()

#一文字ごとencoderで処理する。1文字ごとにblankを挿入して区切る
for char in str:
    enc.encode(char)
    enc.blank()
enc.blank()
print(len(enc.get()))

#音声ファイルを保存する。
enc.save()
