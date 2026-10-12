from native_work import *
import sys, numpy as np
a,b=sys.argv[1:3]
pa,pb=patch(a),patch(b)
ia=Image.open(ZONE/'native'/f'{a}.png').convert('RGB'); ib=Image.open(ZONE/'native'/f'{b}.png').convert('RGB')
assert ia.size==ib.size==(1254,1254)
qa,qb=pa['coreWorldBox'],pb['coreWorldBox']
if qb[0]-qa[0]==1024 and qa[1]==qb[1]:
    out=Image.new('RGB',(512,1024)); out.paste(ia.crop((883,115,1139,1139)),(0,0)); out.paste(ib.crop((115,115,371,1139)),(256,0))
    da=np.array(ia.crop((1024,0,1254,1254)),dtype=float); db=np.array(ib.crop((0,0,230,1254)),dtype=float)
    direction='horizontal_neighbors_vertical_join'
elif qb[1]-qa[1]==1024 and qa[0]==qb[0]:
    out=Image.new('RGB',(1024,512)); out.paste(ia.crop((115,883,1139,1139)),(0,0)); out.paste(ib.crop((115,115,1139,371)),(0,256))
    da=np.array(ia.crop((0,1024,1254,1254)),dtype=float); db=np.array(ib.crop((0,0,1254,230)),dtype=float)
    direction='vertical_neighbors_horizontal_join'
else: raise ValueError('Not directly adjacent')
ident=a+'__'+b; dest=ZONE/'qa'/f'{ident}.join-100pct.png'; out.save(dest)
rec={'seamId':ident,'direction':direction,'a':{'path':(ZONE/'native'/f'{a}.png').as_posix(),'sha256':sha(ZONE/'native'/f'{a}.png'),'nativeWorldBox':pa['nativeWorldBox']},'b':{'path':(ZONE/'native'/f'{b}.png').as_posix(),'sha256':sha(ZONE/'native'/f'{b}.png'),'nativeWorldBox':pb['nativeWorldBox']},'coverageGapPixels':0,'sharedNativeWidth':230,'overlapMeanAbsoluteChannelDifference':float(np.abs(da-db).mean()),'inspectionScale':1,'resized':False,'blending':'none; exact core crops concatenated','inspectionEvidencePath':dest.as_posix(),'status':'pending_visual_review','geometryChecks':{},'reviewedAtUtc':None}
write(ZONE/'qa'/f'{ident}.json',rec)
print(json.dumps(rec))
