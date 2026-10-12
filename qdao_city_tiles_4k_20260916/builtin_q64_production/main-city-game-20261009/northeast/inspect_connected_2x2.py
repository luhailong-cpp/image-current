"""Export 1:1 seam windows from four completed candidates, plus labeled preview.
No source, formal tile, or acceptance metadata is changed.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import json, hashlib, argparse
ZONE=Path(__file__).resolve().parent
OUT=ZONE/'qa/connected-2x2-20261010'
IDS=['r05_c13','r05_c14','r06_c13','r06_c14']
parser=argparse.ArgumentParser()
parser.add_argument('--candidate', action='append', default=[], help='Read-only QA source override: TILE=absolute PNG path')
args=parser.parse_args()
overrides={}
for item in args.candidate:
    tid, path=item.split('=',1)
    assert tid in IDS and tid not in overrides
    path=Path(path).resolve()
    assert path.is_relative_to(ZONE.resolve())
    overrides[tid]=path
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savej(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources={}
ims={}
for tid in IDS:
    f=overrides.get(tid,ZONE/tid/'candidates'/f'{tid}.candidate.png')
    if not f.exists(): raise SystemExit(f'Candidate not ready: {tid}')
    h=sha(f)
    im=Image.open(f); im.load()
    assert im.size==(4096,4096)
    assert im.mode=='RGB' or (im.mode=='RGBA' and im.getextrema()[3]==(255,255))
    ims[tid]=im.convert('RGB')
    sources[tid]={'file':str(f),'sha256':h,'nativeDimensions':[4096,4096]}
signature=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()[:20]
out=OUT/signature
out.mkdir(parents=True,exist_ok=True)
exports=[]
starts=[0,1024,2048,2842]
def output(im,name,kind,recipe):
    p=out/name; im.save(p)
    exports.append({'file':str(p),'sha256':sha(p),'dimensions':list(im.size),'kind':kind,'operation':recipe})
for a,b,label in [('r05_c13','r05_c14','north-west-east'),('r06_c13','r06_c14','south-west-east')]:
    for i,y in enumerate(starts):
        im=Image.new('RGB',(1024,1254))
        im.paste(ims[a].crop((3584,y,4096,y+1254)),(0,0))
        im.paste(ims[b].crop((0,y,512,y+1254)),(512,0))
        output(im,f'{label}-{i+1}-100pct.png','vertical shared edge, seam x512',{'integerCrops':[{a:[3584,y,4096,y+1254]},{b:[0,y,512,y+1254]}],'resampling':False})
for a,b,label in [('r05_c13','r06_c13','west-north-south'),('r05_c14','r06_c14','east-north-south')]:
    for i,x in enumerate(starts):
        im=Image.new('RGB',(1254,1024))
        im.paste(ims[a].crop((x,3584,x+1254,4096)),(0,0))
        im.paste(ims[b].crop((x,0,x+1254,512)),(0,512))
        output(im,f'{label}-{i+1}-100pct.png','horizontal shared edge, seam y512',{'integerCrops':[{a:[x,3584,x+1254,4096]},{b:[x,0,x+1254,512]}],'resampling':False})
im=Image.new('RGB',(1254,1254))
for tid,crop,xy in [('r05_c13',(3469,3469,4096,4096),(0,0)),('r05_c14',(0,3469,627,4096),(627,0)),('r06_c13',(3469,0,4096,627),(0,627)),('r06_c14',(0,0,627,627),(627,627))]:
    im.paste(ims[tid].crop(crop),xy)
output(im,'central-intersection-100pct.png','four-tile shared intersection','four integer 627-square corner crops, no resampling')
preview=Image.new('RGB',(2048,2090),'#14242c')
for tid,xy in zip(IDS,[(0,42),(1024,42),(0,1066),(1024,1066)]):
    preview.paste(ims[tid].resize((1024,1024),Image.Resampling.LANCZOS),xy)
draw=ImageDraw.Draw(preview)
draw.text((18,14),'2x2 CONNECTED ART CANDIDATES / 25% PREVIEW / NOT FINAL NATIVE TILE',fill='white')
output(preview,'connected-2x2-preview.png','25 percent inspection preview, not native deliverable',{'resampling':'LANCZOS downsample per4096tile to1024','nativeSourcesUnchanged':True})
for tid,s in sources.items(): assert sha(s['file'])==s['sha256'],f'Source changed during export: {tid}'
report={'generatedAt':datetime.now(timezone.utc).isoformat(),'status':'exported_for_visual_review_not_acceptance','signature':signature,'sources':sources,'worldBox':[49152,16384,57344,24576],'seams':[{'pair':[a,b]} for a,b in [('r05_c13','r05_c14'),('r06_c13','r06_c14'),('r05_c13','r06_c13'),('r05_c14','r06_c14')]],'nativeSeamWindows':17,'exports':exports,'formalAcceptedCount':0}
savej(out/'manifest.json',report)
savej(OUT/'latest.json',{'manifest':str(out/'manifest.json'),'signature':signature,'preview':str(out/'connected-2x2-preview.png')})
print(json.dumps({'manifest':str(out/'manifest.json'),'preview':str(out/'connected-2x2-preview.png'),'nativeSeamWindows':17}))
