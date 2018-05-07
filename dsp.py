import wave
import numpy as np
import struct
from pylab import *

class encoder:
    def __init__(self):
        self.A=1 #振幅
        self.fs=44100 #サンプリング周波数
        self.clock=100 #基準クロック
        self.swav=[] #音声バッファ
        self.high_frequency = 2500 #1のとき
        self.low_frequency = 2000 #0のとき

    #文字を音声に変換する
    def encode(self,char):
        char_bin = bin(ord(char))[2:] #文字コードを2進数で表したときの0bを取り除く
        print("Decoding:"+char)
        #1bitずつ音声に変換する
        for bit in char_bin:
            print("Binary:"+bit)
            for n in np.arange(int(self.fs/self.clock)):
            #サイン波を生成
                if bit == "1":
                    s = self.A * np.sin(2.0 * np.pi * self.high_frequency * n / self.fs)
                else:
                    s = self.A * np.sin(2.0 * np.pi * self.low_frequency * n / self.fs)
                #音声バッファに追加する
                self.swav.append(s)

    #無音空白生成用関数
    def blank(self):
            for n in np.arange(int(self.fs/self.clock)):
                self.swav.append(0)

    #音声バッファから音声ファイルへと保存する
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
    
    #音声バッファ取得用関数
    def get(self):
        return self.swav

#音声ファイルから文字列へと変換するクラス
class decoder:

    def __init__(self):
        wf = wave.open("output.wav" , "r" ) #音声ファイルを開く
        self.fs = 44100  # サンプリング周波数
        self.x = wf.readframes(wf.getnframes())
        self.x = frombuffer(self.x, dtype= "int16") / 32768.0  # -1 - +1に正規化
        wf.close()
        self.clock = 100
        self.bit_frames = int(self.fs/self.clock)
        self.start = 0  # サンプリングする開始位置
        self.N = self.bit_frames   # FFTのサンプル数
        self.window_func = np.hamming(self.N) #窓関数を利用することでFFTの精度を高める
        self.freq_config() #解析周波数帯や周波数データの切り出し範囲を設定する。
        self.char_data = "0b0" #取り除いた文字コードの先頭部分を付け足す用

    def freq_config(self):
        self.index_max=0 #解析周波数帯の上限
        self.index_min=0 #解析周波数帯の下限
        self.delta_f = 100 #解析周波数幅
        self.high_bit_upper_index=0; #1ビットの周波数帯の上限
        self.high_bit_lower_index=0; #1ビットの周波数帯の下限
        self.low_bit_upper_index=0; #0ビットの周波数帯の上限
        self.low_bit_lower_index=0; #0ビットの周波数帯の下限
        self.freqList = np.fft.fftfreq(self.N, d=1.0/self.fs) #解析する範囲の周波数の目盛りを取得
        index = 0
        #1000Hz以下300Hz以上の必要ない部分をカット
        #2000Hzと2500Hz成分抽出用のindexを取得
        for item in self.freqList: #目盛りを1つずつ読み出す
            index += 1
            if item < 1000:
                self.index_min = index
            if item >= 1000 and item < 2000-self.delta_f:
                self.low_bit_lower_index = index - self.index_min
            if item >= 2000-self.delta_f and item <= 2000+self.delta_f:
                self.low_bit_upper_index = index - self.index_min
            if item > 2000+self.delta_f and item < 2500-self.delta_f:
                self.high_bit_lower_index = index - self.index_min
            if item >= 2500-self.delta_f and item <= 2500+self.delta_f:
                self.high_bit_upper_index = index - self.index_min
            if item > 2500+self.delta_f and item <= 3000:
                self.index_max = index
            if item > 3000:
                break;
        self.string_buffer = ""
        self.freqList = self.freqList[self.index_min:self.index_max] #指定した解析周波数帯を切り出す

    def fft(self,data): #FFTを実行する関数
        if len(self.window_func) == len(data):
            X = np.fft.fft(data*self.window_func)  # FFT
            res = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in X][self.index_min:self.index_max]  # 振幅スペクトル
            return res #実行結果を戻す

    def parse_signal(self,data):#それぞれの周波数帯で総和したデータからビットが0か1か空白かを判定する
        if data[0] > 150:
            return 0
        elif data[1] > 150:
            return 1
        else:
            return -1

    def sum_signal(self,data):#0ビットの周波数帯と1ビットの周波数帯のそれぞれで指定した範囲の周波数成分を総和する
        low_sum = sum(data[self.low_bit_lower_index:self.low_bit_upper_index])
        high_sum = sum(data[self.high_bit_lower_index:self.high_bit_upper_index])
        print("LowBit:"+str(low_sum))
        print("HighBit:"+str(high_sum))
        return low_sum,high_sum

    def graph_draw(self,data):#グラフ描画用。本当は必要ない。処理が重い。
        clf()
        axis([1000, 4000, 0, 50])
        xlabel("frequency [Hz]")
        ylabel("amplitude spectrum")
        plot(self.freqList, data,linestyle='-')
        pause(.01)

    def decode(self,bit):#処理したビットを文字コードへと変換する。1,0ビットの場合はバッファの末尾に付け足し、空白の場合は2進数を文字コードへと変換する。
        if bit == 0:
            print("0")
            self.char_data += "0"
        elif bit == 1:
            print("1")
            self.char_data += "1"
        else:
            buff = chr(int(self.char_data,2))
            print(buff)
            self.string_buffer += buff
            self.char_data = "0b0"

    def start_detection(self):#信号が始まるポイントを探す。
        start_flag = False
        num = 0
        while(not(start_flag) and len(self.x) > num*10):
            start = num*10
            spectrum_data = self.fft(self.x[start:start+self.N])
            sig_sum = self.sum_signal(spectrum_data)
            if((sig_sum[0] > 150 or sig_sum[1] > 150) and abs(sig_sum[0] - sig_sum[1]) > 220):
                start_flag = True
            num += 1
        return num*10

    def begin(self,start_point):#上記の関数を利用して文字を1つずつ取得する。
        data = self.x[start_point:]
        for i in range(int(len(data)/self.bit_frames)):#Nの範囲ずつFFTで処理する。1ビット分の周波数データ数をNとして1ビットずつ処理している。
            start = i*self.N #FFT開始点の決定
            spectrum_data = self.fft(data[start:start+self.N]) #FFTを実行
            self.graph_draw(spectrum_data) #グラフを描画。本当は必要ない
            sig_sum = self.sum_signal(spectrum_data) #各周波数帯成分の総和を取る
            bit = self.parse_signal(sig_sum) #ビットの判定
            self.decode(bit) #文字列への変換

    def get_string(self): #バッファーの文字列を取得する。
        return self.string_buffer

