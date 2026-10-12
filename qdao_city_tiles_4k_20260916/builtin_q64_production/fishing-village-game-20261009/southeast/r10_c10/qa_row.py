"""Unscaled native seam strips and a cropped candidate row; never modifies art."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

TILE=Path(__file__).resolve().parent
ZONE=TILE.parent
QA=TILE/'qa'
QA.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
selected=read(TILE/'selected-patches.json')
sources=[ZONE/'r10_c09'/'native'/'p14-v3.png']+[TILE/selected['patches'][f'p1{c}'] for c in range(1,5)]
identities=['r10_c09_p14']+[f'r10_c10_p1{c}' for c in range(1,5)]
records=[]
for i in range(4):
    left,right=[Image.open(p).convert('RGB') for p in sources[i:i+2]]
    assert left.size==right.size==(1254,1254)
    combined=Image.new('RGB',(2278,1254))
    combined.paste(left.crop((0,0,1139,1254)),(0,0))
    combined.paste(right.crop((115,0,1254,1254)),(1139,0))
    name=f'{identities[i]}--{identities[i+1]}'
    pair=QA/f'{name}-pair-native.png'
    strip=QA/f'{name}-seam-native.png'
    combined.save(pair)
    combined.crop((883,0,1395,1254)).save(strip)
    a=np.asarray(left,dtype=np.int16);b=np.asarray(right,dtype=np.int16)
    record={'id':name,'leftSource':{'path':str(sources[i]),'sha256':sha(sources[i])},'rightSource':{'path':str(sources[i+1]),'sha256':sha(sources[i+1])},'pair':str(pair),'pairSha256':sha(pair),'strip':str(strip),'stripSha256':sha(strip),'classification':'QA only; no geometry/color correction applied','operation':'unscaled crops and hard join at native overlap midpoint','overlapPixels':230,'coreCut':115,'pairDimensions':[2278,1254],'stripDimensions':[512,1254],'stripSeamX':256,'meanPixelStepAtCoreJoin':float(np.abs(a[:,1138]-b[:,115]).mean()),'meanOverlapAbsoluteDifference':float(np.abs(a[:,1024:1254]-b[:,:230]).mean()),'visualStatus':'pending','externalSourceMayBeSuperseded':i==0}
    write(pair.with_suffix('.png.derivation.json'),record)
    write(strip.with_suffix('.png.derivation.json'),record)
    records.append(record)
row=Image.new('RGB',(4096,1024))
contributions=[]
for i,p in enumerate(sources[1:]):
    image=Image.open(p)
    crop=[115,115,1139,1139]
    row.paste(image.crop(crop),(i*1024,0))
    contributions.append({'source':str(p),'sha256':sha(p),'crop':crop,'destination':[i*1024,0,(i+1)*1024,1024],'operation':'unscaled core crop/paste'})
row_path=QA/'r10_c10-first-row-candidate-4096x1024.png'
row.save(row_path)
write(row_path.with_suffix('.png.derivation.json'),{'file':str(row_path),'sha256':sha(row_path),'classification':'partial candidate row for QA only, not accepted tile','dimensions':[4096,1024],'resizeApplied':False,'sources':contributions})
preview=QA/'r10_c10-first-row-preview-1024x256.png'
row.resize((1024,256),Image.Resampling.LANCZOS).save(preview)
write(preview.with_suffix('.png.derivation.json'),{'file':str(preview),'sha256':sha(preview),'classification':'downsampled QA preview only','derivedFrom':{'path':str(row_path),'sha256':sha(row_path)},'operation':'LANCZOS downsample for inspection','dimensions':[1024,256]})
summary={'tile':'r10_c10','createdAt':datetime.now(timezone.utc).isoformat(),'selectedNativeCount':4,'complete4kCount':0,'formalAcceptedCount':0,'seams':records,'rowCandidate':str(row_path),'preview':str(preview),'externalSourceRecheckRequired':True}
write(QA/'first-row-qa.json',summary)
print(json.dumps({'seams':[{'id':r['id'],'meanStep':r['meanPixelStepAtCoreJoin']} for r in records],'preview':str(preview)},ensure_ascii=False,indent=2))
