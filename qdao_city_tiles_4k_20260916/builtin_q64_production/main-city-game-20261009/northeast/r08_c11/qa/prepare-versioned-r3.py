from pathlib import Path
from PIL import Image
import json,sys,hashlib,importlib.util
p=Path(__file__).resolve().parents[1];z=p.parent
spec=importlib.util.spec_from_file_location('w',z/'tile_worker.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w);w.setup(p.name)
patch,ver,desc=sys.argv[1:4];assert ver.startswith(patch+'-')
coord=next(c for c in json.loads((p/'coordinates.json').read_text())['patches'] if c['id']==patch)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
src=Path(coord['guide']);assert sha(src)==coord['guideSha256'];im=Image.open(src).convert('RGB');derived=[{'file':str(src),'sha256':sha(src),'role':'layout-only blur'}];adj=[]
for direction,nt,np,box,pos in w.neighbors(patch):
 f=w.p.selected_native(nt,np)
 if not f.exists():continue
 m=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf-8-sig'));assert sha(f)==m['sha256'];im.paste(Image.open(f).convert('RGB').crop(box),pos)
 derived.append({'file':str(f),'sha256':sha(f),'role':'actual '+direction+' native context','crop':list(box),'paste':list(pos)})
 if nt!=p and nt not in adj:adj.append(nt)
wx,wy,wr,wb=coord['contextWorldBox']
for nt in adj:
 pf=nt/'tile-progress.json';pr=json.loads(pf.read_text(encoding='utf-8-sig')) if pf.exists() else {};f=Path(pr['candidate']) if pr.get('candidate') else nt/'candidates'/f'{nt.name}.candidate.png'
 if not f.exists():continue
 assert f.resolve().is_relative_to(nt.resolve());_,_,ox,oy=w.p.tile_coordinates(nt.name);x0,y0,x1,y1=max(wx,ox),max(wy,oy),min(wr,ox+4096),min(wb,oy+4096)
 if x1<=x0 or y1<=y0:continue
 box=[x0-ox,y0-oy,x1-ox,y1-oy];pos=[x0-wx,y0-wy];im.paste(Image.open(f).convert('RGB').crop(box),tuple(pos));derived.append({'file':str(f),'sha256':sha(f),'role':'current candidate core pixels, not acceptance','crop':box,'paste':pos})
target=p/'layout-only'/f'{ver}-mixed-context.png';assert not target.exists();im.save(target);Path(str(target)+'.generation.json').write_text(json.dumps({'derivedFrom':derived,'operation':'integer crop paste only, no resizing','sha256':sha(target)},indent=2),encoding='utf-8')
req=json.loads((p/'prompts/p32-v20261013-r2.request.json').read_text());req['referenced_image_paths'][0]=str(target)
req['prompt']='Use case: precise-object-edit. Complete Image1 as one continuous native1254x1254 opaque game-map painting. Its sharp outer230px strips are real adjacent native art: their positions, stone endpoint geometry and material are fixed. The blurred interior is ONLY a geometry placeholder; paint it into crisp new native detail. '+desc+' Integrate the interior seamlessly with every fixed strip. No straight rectangular cut or strip outline may remain within the image. Preserve camera, crop, scale and the established layout; soft upper-left daylight and approved Daoist Q hand-painted style. Images2/3/4 are supporting approved geography, daylight material detail and primary style respectively. Do not import their composition. No extra objects, plants, structures, decorative floor stripe, text, UI, frame, watermark, blur, enlargement or resampling.'
for s,t in [('request.json',json.dumps(req,indent=2)),('prompt.txt',req['prompt'])]:
 f=p/'prompts'/f'{ver}.{s}';assert not f.exists();f.write_text(t,encoding='utf-8')
print(json.dumps(req))
