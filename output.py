from dsp import decoder

dec = decoder()
start_point = dec.start_detection()
print("Start Point:"+str(start_point))
dec.begin(start_point)
print(dec.get_string())
