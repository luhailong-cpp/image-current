"""Create an explicit current manifest and unchanged-coordinate context crop.
Context is reference/inspection only and never final game artwork.
"""
from pathlib import Path
import argparse, json, hashlib
from PIL import Image
ap=argparse.ArgumentParser()
ap.add_argument('--cluster',required=True)
ap.add_argument('--output-manifest',required=True)
ap.add_argument('--context-box',nargs=4,type=int,required=True)
ap.add_argument('--context-stem',required=True)
a=ap.parse_args()
info=lambda p:dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
cp=Path(a.cluster).resolve();data=json.loads(cp.read_text(encoding='utf8'))
manifest=dict(schemaVersion=1,tiles=[])
x0,y0,x1,y1=a.context_box
assert 0<=x0<x1<=8192 and 0<=y0<y1<=8192
canvas=Image.new('RGB',(x1-x0,y1-y0));parts=[];covered=0
for index,item in enumerate(data['outputs']):
 im=Path(item['output']['path']);rec=Path(item['projectionRecordPath'])
 assert info(im)['sha256']==item['output']['sha256']
 manifest['tiles'].append(dict(tileId=item['tileId'],image=info(im),record=info(rec)))
 ox=(index%2)*4096;oy=(index//2)*4096
 left,top,right,bottom=max(x0,ox),max(y0,oy),min(x1,ox+4096),min(y1,oy+4096)
 if right<=left or bottom<=top:continue
 box=[left-ox,top-oy,right-ox,bottom-oy]
 with Image.open(im) as source:
  assert source.size==(4096,4096)
  canvas.paste(source.crop(box),(left-x0,top-y0))
 covered+=(right-left)*(bottom-top)
 parts.append(dict(tileId=item['tileId'],source=info(im),cropBox=box,destination=[left-x0,top-y0]))
assert covered==(x1-x0)*(y1-y0)
mp=Path(a.output_manifest).resolve();stem=Path(a.context_stem).resolve()
output=stem.with_suffix('.png');derivation=stem.with_suffix('.derivation.json')
assert not mp.exists() and not output.exists() and not derivation.exists()
with mp.open('x',encoding='utf8') as f:json.dump(manifest,f,indent=2)
with output.open('xb') as f:canvas.save(f,format='PNG')
proof=dict(schemaVersion=1,operation='unchanged-coordinate native context crop',isAiGeneration=False,role='full object reference and inspection only; not a final-art source',cluster=info(cp),manifest=info(mp),clusterCropBox=a.context_box,dimensions=list(canvas.size),parts=parts,output=info(output),resizing=False,pixelSynthesis=False)
with derivation.open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
print(json.dumps(dict(manifest=info(mp),context=info(output),derivation=info(derivation)),indent=2))
