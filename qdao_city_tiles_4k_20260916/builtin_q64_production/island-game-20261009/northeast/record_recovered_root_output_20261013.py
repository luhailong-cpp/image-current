from native_work import *
p=ZONE/'native/r03_c09_p02_04.png.generation.json';d=read(p)
d['evidence']['fields']=['recovered_originalToolPath','source_file_timestamp','single_inflight_call','visual_anchor_match']
d['evidence']['receiptRecovered']=True;d['evidence']['originalToolOutputHintAvailable']=False
write(p,d)
print(d['sha256'])
