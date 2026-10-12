import json,hashlib,sys
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parents[1]
patch,version=sys.argv[1:3]
stem='r10_c04_'+patch+'_'+version
reqp=Z/'native'/f'{stem}.request.json'
req=json.loads(reqp.read_text(encoding='utf-8-sig'))
box=req['coordinates']['globalContextBox']
canvas=Image.open(Z/'layout-only'/f'r10_c04_{patch}.png').convert('RGB')
pr=int(patch[1:3])
sources=[]
for rp in sorted((Z/'native').glob('*.png.generation.json')):
 r=json.loads(rp.read_text(encoding='utf-8-sig'))
 if r.get('status') in ['rejected','superseded','frozen_upstream_geometry_repair']:continue
 sb=r.get('coordinates',{}).get('globalContextBox')
 if not sb or r.get('coordinates',{}).get('role','').startswith('localized'):continue
 fn=Path(r['file']).stem
 allowed=fn.startswith('r09_c04_p04_') if pr==1 else fn.startswith('r10_c04_p%02d_'%(pr-1))
 allowed=allowed or fn.startswith('r10_c04_p%02d_02_'%pr) or fn.startswith('r10_c04_p%02d_04_'%pr)
 if not allowed:continue
 inter=[max(box[0],sb[0]),max(box[1],sb[1]),min(box[2],sb[2]),min(box[3],sb[3])]
 if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
 if inter[2]-inter[0]>230 and inter[3]-inter[1]>230:continue
 canvas.paste(Image.open(r['file']).crop((inter[0]-sb[0],inter[1]-sb[1],inter[2]-sb[0],inter[3]-sb[1])),(inter[0]-box[0],inter[1]-box[1]))
 sources.append({'path':r['file'],'sha256':r['sha256'],'globalOverlapBox':inter,'role':'specified upper/left/right native boundary; known wrong lower neighbor excluded'})
p=Z/'layout-only'/f'{stem}_continuity.png';canvas.save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
Path(str(p)+'.derivation.json').write_text(json.dumps({'file':p.as_posix(),'sha256':sha(p),'role':'selective native continuity guide; enlarged layout is guidance only','operation':'integer crop/paste native; no native resampling','baseGuide':str(Z/'layout-only'/f'r10_c04_{patch}.png'),'nativeSources':sources},indent=2)+'\n',encoding='utf8')
req['overlaps']=sources
reqp.write_text(json.dumps(req,indent=2)+'\n',encoding='utf8')
print(p.as_posix())
