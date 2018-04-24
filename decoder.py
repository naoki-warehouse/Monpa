#coding:utf-8
import wave
import numpy as np
from pylab import *

class decoder:

    def __init__(self):
        wf = wave.open("output.wav" , "r" )
        self.fs = 44100  # サンプリング周波数
        self.x = wf.readframes(wf.getnframes())
        self.x = frombuffer(self.x, dtype= "int16") / 32768.0  # -1 - +1に正規化
        wf.close()
        self.clock = 100
        self.bit_frames = int(self.fs/self.clock)
        self.start = 0  # サンプリングする開始位置
        self.N = self.bit_frames   # FFTのサンプル数
        self.window_func = np.hamming(self.N) #窓関数で検索！
        self.freq_config()
        self.char_data = "0b0"

    def freq_config(self):
        self.index_max=0
        self.index_min=0
        self.delta_f = 100
        self.high_bit_upper_index=0;
        self.high_bit_lower_index=0;
        self.low_bit_upper_index=0;
        self.low_bit_lower_index=0;
        self.freqList = np.fft.fftfreq(self.N, d=1.0/self.fs)
        index = 0
        #1000Hz以下300Hz以上の必要ない部分をカット
        #2000Hzと2500Hz成分抽出用のindexを取得
        for item in self.freqList:
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
        self.char_data="0b"
        self.string_buffer = ""
        self.freqList = self.freqList[self.index_min:self.index_max]

    def fft(self,data):
        if len(self.window_func) == len(data):
            X = np.fft.fft(data*self.window_func)  # FFT
            res = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in X][self.index_min:self.index_max]  # 振幅スペクトル
            return res

    def parse_signal(self,data):
        if data[0] > 150:
            return 0
        elif data[1] > 150:
            return 1
        else:
            return -1

    def sum_signal(self,data):
        low_sum = sum(data[self.low_bit_lower_index:self.low_bit_upper_index])
        high_sum = sum(data[self.high_bit_lower_index:self.high_bit_upper_index])
        print("LowBit:"+str(low_sum))
        print("HighBit:"+str(high_sum))
        return low_sum,high_sum

    def graph_draw(self,data):
        clf()
        axis([1000, 4000, 0, 50])
        xlabel("frequency [Hz]")
        ylabel("amplitude spectrum")
        plot(self.freqList, data,linestyle='-')
        pause(.01)

    def decode(self,bit):
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

    def start_detection(self):
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
    def begin(self,start_point):
        data = self.x[start_point:]
        for i in range(int(len(data)/self.bit_frames)):
            start = i*self.N
            spectrum_data = self.fft(data[start:start+self.N])
            self.graph_draw(spectrum_data)
            sig_sum = self.sum_signal(spectrum_data)
            bit = self.parse_signal(sig_sum)
            self.decode(bit)

    def get_string(self):
        return self.string_buffer

dec = decoder()
start_point = dec.start_detection()
print(start_point)
dec.begin(start_point)
print(dec.get_string())
