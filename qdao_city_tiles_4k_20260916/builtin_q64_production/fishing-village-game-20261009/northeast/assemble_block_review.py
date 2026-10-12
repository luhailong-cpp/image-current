"""Create exact 2x2 candidate QA from an explicit four-tile selection.

Usage: bundled-python assemble_block_review.py records/first-block.selection.json v1
Selection: {"tiles":{"r06_c12":{"path":"tiles/...png","sha256":"..."},...}}
No automatic visual approval; all final art assembly is integer crop/paste.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
from PIL import Image

Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selection=Path(sys.argv[1]);selection=selection if selection.is_absolute() else Z/selection
version=sys.argv[2]
assert re.fullmatch('[a-zA-Z0-9_-]+',version)
chosen=read(selection)['tiles']
expected=['r06_c12','r06_c13','r07_c12','r07_c13']
assert set(chosen)==set(expected),'Explicit first 2x2 only'
q=Z/'qa'/f'first-block-{version}'
assert not q.exists(),'Versioned QA directory already exists'
canvas=Image.new('RGB',(8192,8192)); sources=[]
for i,t in enumerate(expected):
    item=chosen[t];p=Path(item['path']);p=p if p.is_absolute() else Z/p
    assert p.resolve().is_relative_to((Z/'tiles').resolve())
    assert sha(p)==item['sha256']
    side=Path(str(p)+'.derived.json');record=read(side)
    origin=[(int(t[5:])-1)*4096,(int(t[1:3])-1)*4096]
    expected_box=origin+[origin[0]+4096,origin[1]+4096]
    recorded_box=record.get('nativeGlobalBox')
    if recorded_box is None and record.get('origin')==origin:
        assert record.get('dimensions')==[4096,4096]
        recorded_box=expected_box
    assert recorded_box==expected_box
    im=Image.open(p);im.load();assert im.size==(4096,4096)
    x,y=(i%2)*4096,(i//2)*4096
    canvas.paste(im.convert('RGB'),(x,y))
    assert canvas.crop((x,y,x+4096,y+4096)).tobytes()==im.convert('RGB').tobytes()
    sources.append({'tile':t,'path':str(p),'sha256':sha(p),'record':{'path':str(side),'sha256':sha(side)},'destinationBox':[x,y,x+4096,y+4096]})
q.mkdir(parents=True)
entries=[]
for axis in ['vertical','horizontal']:
    for half in range(2):
        for seg in range(4):
            k=half*4096+seg*1024
            b=[3968,k,4224,k+1024] if axis=='vertical' else [k,3968,k+1024,4224]
            out=q/f'{axis}_half{half+1}_segment{seg+1}.native-1to1.png'
            canvas.crop(b).save(out)
            entries.append({'file':str(out),'sha256':sha(out),'kind':axis,'blockCropBox':b,'pixelScale':1,'seamLocalCoordinate':128,'completeSharedEdgeSegmentPixels':1024,'visualReview':'pending','formalAccepted':False})
b=[3840,3840,4352,4352];out=q/'four_tile_junction.native-1to1.png';canvas.crop(b).save(out)
entries.append({'file':str(out),'sha256':sha(out),'kind':'four_tile_junction','blockCropBox':b,'pixelScale':1,'visualReview':'pending','formalAccepted':False})
preview=q/'first-block.preview-only-2048.png';canvas.resize((2048,2048),Image.Resampling.LANCZOS).save(preview)
for s in sources:assert sha(s['path'])==s['sha256'],'Source changed during review assembly'
save(q/'manifest.json',{'selection':{'path':str(selection),'sha256':sha(selection)},'sources':sources,'qa':entries,'previewOnly':{'path':str(preview),'sha256':sha(preview),'pixels':[2048,2048],'notFinalArt':True},'operation':'Exact integer paste and native strip crops; only preview is downsampled.','mechanicalChecksPassed':True,'externalEdgesInspected':False,'formalAccepted':False})
print(json.dumps({'manifest':str(q/'manifest.json'),'externalBoundarySegments':16,'fourTileJunctions':1,'formalAccepted':False}))
