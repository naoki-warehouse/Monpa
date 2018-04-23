#coding:utf-8
import wave
import numpy as np
from pylab import *

if __name__ == "__main__" :
    wf = wave.open("output.wav" , "r" )
    fs = 44100  # サンプリング周波数
    x = wf.readframes(wf.getnframes())
    x = frombuffer(x, dtype= "int16") / 32768.0  # -1 - +1に正規化
    wf.close()
    clock = 100
    bit_frames = int(fs/clock)
    start = 0  # サンプリングする開始位置
    N = bit_frames   # FFTのサンプル数
    window_func = np.hamming(N) #窓関数で検索！
    data = x[start:start+N]

    #1000Hz以下4000Hz以上の必要ない部分をカット
    #2000Hzと3500Hz成分抽出用のindexを取得
    index_max=0
    index_min=0
    delta_f = 100
    high_bit_upper_index=0;
    high_bit_lower_index=0;
    low_bit_upper_index=0;
    low_bit_lower_index=0;
    freqList = np.fft.fftfreq(N, d=1.0/fs)
    index = 0
    for item in freqList:
        index += 1
        if item < 1000:
            index_min = index
        if item >= 1000 and item < 2000-delta_f:
            low_bit_lower_index = index - index_min
        if item >= 2000-delta_f and item <= 2000+delta_f:
            low_bit_upper_index = index - index_min
        if item > 2000+delta_f and item < 3500-delta_f:
            high_bit_lower_index = index - index_min
        if item >= 3500-delta_f and item <= 3500+delta_f:
            high_bit_upper_index = index - index_min
        if item > 3500+delta_f and item <= 4000:
            index_max = index
        if item > 4000:
            break;
    char_data="0b"
    string_buffer = ""
    for i in range(int(len(x)/bit_frames)):
        start = i*N
        data = x[start:start+N]
        if len(window_func) == len(data):
            clf()
            X = np.fft.fft(data*window_func)  # FFT
            spectrum = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in X[index_min:index_max]]  # 振幅スペクトル
            # 振幅スペクトルを描画
#            axis([1000, 4000, 0, 50])
#            xlabel("frequency [Hz]")
#            ylabel("amplitude spectrum")
#            freqList = np.fft.fftfreq(N, d=1.0/fs)[index_min:index_max]  # 周波数軸の値を計算
#            plot(freqList, spectrum,linestyle='-')
#            pause(.01)
            low_sum = sum(spectrum[low_bit_lower_index:low_bit_upper_index])
            high_sum = sum(spectrum[high_bit_lower_index:high_bit_upper_index])
            print("LowBit:"+str(low_sum))
            print("HighBit:"+str(high_sum))
            if low_sum > 150:
                print("0")
                char_data += "0"
            elif high_sum > 150:
                print("1")
                char_data += "1"
            else:
                buff = chr(int(char_data,2))
                print(buff)
                string_buffer += buff
                char_data = "0b"
    print(string_buffer)
