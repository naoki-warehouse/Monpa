from dsp import decoder #音声処理ライブラリ

dec = decoder() #decoderインスタンスを作成する
#無音部分を取り除き、信号が始まる部分を探す。
start_point = dec.start_detection()
print("Start Point:"+str(start_point))
#音声ファイルから文字列を変換する
dec.begin(start_point)
#変換した文字列を出力する。
print(dec.get_string())
