# -*- coding: utf-8 -*-
from sin_wave import encoder
from matplotlib import pylab as plt
import struct
import wave
enc = encoder()
num = 0
for i in range(10):
    enc.blank()
    num += 441
print("Blank:"+str(num))
str = input()
for char in str:
    enc.encode(char)
    enc.blank()
enc.blank()
print(len(enc.get()))
swav = enc.save()
#plt.plot(swave[0:5000])
#plt.show()
