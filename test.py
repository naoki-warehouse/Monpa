# -*- coding: utf-8 -*-
from sin_wave import encoder
from matplotlib import pylab as plt
import struct
import wave
enc = encoder()
str = input()
for char in str:
    enc.encode(char)
    enc.blank()
print(len(enc.get()))
swav = enc.save()
#plt.plot(swave[0:5000])
#plt.show()
