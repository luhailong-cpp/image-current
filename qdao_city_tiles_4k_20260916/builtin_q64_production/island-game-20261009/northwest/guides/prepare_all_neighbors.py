from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,argparse
Z=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser(); ap.add_argument('--row',type=int,required=True); ap.add_argument('--col',type=int,required=True); ap.add_argument('--attempt',default='a01')
for edge in ['left','right','top','bottom']: ap.add_argument('--'+edge)
a=ap.parse_args(); stem=f'r03_c03_s{a.row:02d}_{a.col:02d}_{a.attempt}'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs=read(Z/'references.json'); x=8192+(a.col-1)*1024; y=8192+(a.row-1)*1024; box=[x-115,y-115,x+1139,y+1139]; rb=[v*1254/57344 for v in box]
im=Image.open(refs[0]['path']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,rb,Image.Resampling.BICUBIC)
neighbor=[]
spec={'left':([1024,0,1254,1254],[0,0]),'right':([0,0,230,1254],[1024,0]),'top':([0,1024,1254,1254],[0,0]),'bottom':([0,0,1254,230],[0,1024])}
for edge,(crop,dest) in spec.items():
 name=getattr(a,edge)
 if not name:continue
 p=Z/'native'/f'{name}.png'; src=Image.open(p).convert('RGB'); assert src.size==(1254,1254)
 im.paste(src.crop(crop),tuple(dest))
 neighbor.append(dict(path=p.as_posix(),sha256=sha(p),role=f'{edge} adjacent selected native with exact 230px overlap',sourceCrop=crop,destination=dest,nativeSize=[1254,1254]))
out=Z/'guides'/f'{stem}.layout-with-native.png'; assert not out.exists(); im.save(out)
rec=dict(stem=stem,globalBox=box,coreBox=[x,y,x+1024,y+1024],referenceBox=rb,inputs=[dict(path=out.as_posix(),sha256=sha(out),role='layout-only plus explicitly selected native neighbor strips on all existing sides',nativeSize=[1254,1254])]+refs+neighbor,neighbor=neighbor,layoutPixelsForbiddenInFinal=True,operation='floating extent layout guide plus unresampled selected native overlap paste; corners follow left-right-top-bottom order',missingEdges=[e for e in spec if not getattr(a,e)])
write(Z/'guides'/f'{stem}.input.json',rec)
state=read(Z/'progress.json');state.update(status='preparing_native',currentPatch=stem,nextStep='Inspect guide and generate with all recorded existing native neighbors.',updatedAtUtc=datetime.now(timezone.utc).isoformat());write(Z/'progress.json',state)
print(json.dumps(dict(stem=stem,box=box,neighbors=[n['role'] for n in neighbor]),ensure_ascii=False))
