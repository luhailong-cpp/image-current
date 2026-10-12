import json
from PIL import Image
import root_workflow as w
import r06_c14_extension as b
Z=w.Z;Q=Z/'qa'/'r06_c14-v1';L=Z/'tiles'/'r06_c13.candidate-v1.png';R=Z/'tiles'/'r06_c14.candidate-v1.png'
assert b.sha(L)=='8ccfd6ba6b6abc890a4928f8d4a6a2a0496f1ccb72ff50a05d186ae25a2cf891';assert b.sha(R)=='77b80761fa46004fa6de84a4895114e568ae5159f9778d3ba1d90c90e63016b8'
l=Image.open(L).convert('RGB');r=Image.open(R).convert('RGB');items=[]
for kind,i in [('segment',i) for i in range(1,5)]+[('junction',i) for i in range(1,4)]:
 y0=(i-1)*1024 if kind=='segment' else i*1024-256;y1=y0+(1024 if kind=='segment' else 512)
 a=Image.new('RGB',(256,y1-y0));a.paste(l.crop((3968,y0,4096,y1)),(0,0));a.paste(r.crop((0,y0,128,y1)),(128,0));p=Q/f'r06_c14-west-{kind}{i}.native-1to1.png';q=Image.open(p).convert('RGB');assert a.size==q.size and a.tobytes()==q.tobytes()
 items.append(dict(b.ref(p,'root direct native external QA'),pixelEqualityToCurrentCandidates=True,leftCrop=[3968,y0,4096,y1],rightCrop=[0,y0,128,y1],seam=128))
f=Q/'root-west-review-complete-20261012.json';assert not f.exists();w.atomic(f,{'reviewer':'root','reviewedAtUtc':b.now(),'candidates':[b.ref(L,'west tile'),b.ref(R,'east tile')],'allSevenDirectlyViewed':True,'allSevenExactPixelProvenanceVerified':True,'nativeExternalWestPassed':True,'qa':items,'observations':'Lantern, stone steps, canopy edge, timber and cushion outlines connect. Small painted facets change subtly; no blocking gap or geometric jump.','formalAccepted':False})
p=Q/'internal-review-summary.json';d=json.loads(p.read_text());d['externalWestReview']=b.ref(f,'native west review proof');d['externalWestPassed']=True;w.atomic(p,d)
print(json.dumps({'westSegments':4,'westJunctions':3,'exactPixelsVerified':True,'nativeExternalWestPassed':True}))
