# -*- coding: utf-8 -*-
import wave
import numpy as np
import struct

class encoder:
    def __init__(self):
        self.A=1 #振幅
        self.fs=44100 #サンプリング周波数
        self.clock=100 #基準クロック
        self.swav=[]
        self.high_frequency = 3500 #1のとき
        self.low_frequency = 2000 #0のとき

    def encode(self,char):
        char_bin = bin(ord(char))[2:] #2進数で表したときの0bを取り除く
        print("Decoding:"+char)
        for bit in char_bin:
            print("Binary:"+bit)
            for n in np.arange(int(self.fs/self.clock)):
            #サイン波を生成
                if bit == "1":
                    s = self.A * np.sin(2.0 * np.pi * self.high_frequency * n / self.fs)
                else:
                    s = self.A * np.sin(2.0 * np.pi * self.low_frequency * n / self.fs)
                self.swav.append(s)
    def blank(self):
            for n in np.arange(int(self.fs/self.clock)):
                self.swav.append(0)
    def save(self):
        #サイン波を-32768から32767の整数値に変換(signed 16bit pcmへ)
        swav_pcm = [int(x * 32767.0) for x in self.swav]
        #バイナリ化
        binwave = struct.pack("h" * len(swav_pcm),*swav_pcm)
        #サイン波をwavファイルとして書き出し
        w = wave.Wave_write("output.wav")
        p = (1, 2, 8000, len(binwave), 'NONE', 'not compressed')
        w.setparams(p)
        w.writeframes(binwave)
        w.close()

    def get(self):
        return self.swav

