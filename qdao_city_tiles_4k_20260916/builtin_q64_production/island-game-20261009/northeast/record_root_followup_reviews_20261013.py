from native_work import *
name='r04_c10-native-v1-20261013';q=ZONE/'qa'/f'{name}-final'
files=[q/n for n in ['cross-1-1-100pct.png','cross-3-1-100pct.png','horizontal-3-segment-1-100pct.png']]
p=ZONE/'qa'/f'{name}-root-independent-spotreview-20261013.json';assert not p.exists()
write(p,{'tileId':'r04_c10','candidate':read(ZONE/'selection-r04_c10.json')['candidatePath'],'reviewer':'root','reviewedAtUtc':now(),'scope':'preview and independent 1:1 spot inspection around native cross points and southwest Chinese knot; supplements worker full49 review','status':'passed','images':[{'file':str(f),'sha256':sha(f),'inspectionScale':1,'resized':False,'status':'passed_visual_100pct'} for f in files],'finding':'Diagonal paving geometry, fine stone material and Chinese knot shadow continue across inspected joins.','formalAccepted':False})
for i in range(1,4):
 p=ZONE/'qa'/f'r03c09-c10-cross{i}-20261013.json';d=read(p)
 assert all(sha(Path(s['file']))==s['sha256'] for s in d['sources'])
 d.update(status='passed_visual_100pct',reviewer='root',reviewedAtUtc=now(),reviewBasis='Exact 1:1 image viewed by root before previous context compaction; current source hashes verified unchanged',finding='Continuous stone slab contours and material at four-way boundary; formal full boundary acceptance pending r03_c09 assembly')
 write(p,d)
print('Recorded independent r04_c10 spot review and 3 previously inspected exact-hash r03c09/c10 crossings')

