from pathlib import Path
Q=Path(__file__).resolve().parent
s=(Q/'finish-r10r11c06c07-repair-v2.py').read_text(encoding='utf-8')
s=s.replace("PRE='block2x2-r10r11c06c07-v2'","PRE='block2x2-r10r11c06c07-v3'")
s=s.replace("p=mod('record_local',Z/'production.py');orig=p.write;p.write=lambda path,obj:None if path.name=='progress.json' else orig(path,obj);p.record('r11_c07_north_rail_repair_v1')",'')
s=s.replace(';sel=mask.astype(bool);', ';mask[:,1209:]=mask[:,1208:1209];sel=mask.astype(bool);')
s=s.replace("ids=np.load(t['sourceIds']['path']);ids[y:b,l:r][sel]=3", """ids=np.load(t['sourceIds']['path']);ids[y:b,l:r][sel]=3
rebases=[]
for ri,tid in enumerate(['r10_c06','r11_c06']):
 yoff=ri*4096;sl=out[yoff:yoff+4326,:4326];prior=Q/('pair-r10r11c06-final-v5-'+tid+'-context-native.png');rootp=Q/('block2x2-r10r11c05c06-v1-'+tid+'-context-native.png');old=rgb(prior);new=rgb(rootp);rootdelta=np.any(old!=new,axis=2);ours=np.any(sl!=old,axis=2);overlap=rootdelta&ours
 assert np.array_equal(sl[overlap],new[overlap]),'Conflicting rebase pixels'
 sl[rootdelta]=new[rootdelta];ids[yoff:yoff+4326,:4326][rootdelta]=4+ri
 rebases.append({'tile':tid,'base':ref(prior),'source':ref(rootp),'rootDeltaMask':npy(tid+'-root-west-delta-mask',rootdelta),'conflictingPixels':0,'overlapIdenticalPixels':int(overlap.sum()),'rootPixelCount':int(rootdelta.sum())})
""")
s=s.replace("'repair':{'source'", "'westRebases':rebases,'repair':{'rightBoundary':'native repair chosen through outer block edge within top/bottom mask; no neighbor beyond this context','source'")
s=s.replace("'3':'native rail repair'", "'3':'native rail repair','4':'root r10_c06 west source','5':'root r11_c06 west source'")
p=Q/'finish-r10r11c06c07-repair-v3.py';assert not p.exists();p.write_text(s,encoding='utf-8')
