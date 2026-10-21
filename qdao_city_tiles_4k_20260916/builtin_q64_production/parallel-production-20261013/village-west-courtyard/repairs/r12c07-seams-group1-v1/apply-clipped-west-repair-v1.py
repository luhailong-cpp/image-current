"""Add a native AI repair by hard source selection, without resampling or blending."""
from pathlib import Path
import argparse, importlib.util, json, hashlib, datetime, sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
    p=Path(p)
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()
def image(p):
    a=Image.open(p)
    if a.mode=='RGBA': assert a.getextrema()[3]==(255,255)
    return np.asarray(a.convert('RGB')).copy()
def save(p,a):
    with p.open('xb') as f: Image.fromarray(a).save(f,format='PNG')
    return {'path':p.name,'sha256':sha(p),'dimensions':[a.shape[1],a.shape[0]]}
def savej(p,j):
    with p.open('x',encoding='utf-8') as f: json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')

p=argparse.ArgumentParser(__doc__)
p.add_argument('--base-assembly',required=True)
p.add_argument('--base-sha256',required=True)
p.add_argument('--repair-generation',required=True)
p.add_argument('--repair-generation-sha256',required=True)
p.add_argument('--output-dir',required=True)
p.add_argument('--open-bottom',action='store_true',help='Use repair through bottom halo; only permitted if its bottom equals context bottom')
p.add_argument('--open-top',action='store_true')
p.add_argument('--open-left',action='store_true')
p.add_argument('--open-right',action='store_true')
a=p.parse_args()
bp=resolve(a.base_assembly);gp=resolve(a.repair_generation);out=resolve(a.output_dir)
assert bp.is_relative_to(ROOT) and gp.is_relative_to(ROOT) and out.is_relative_to(ROOT/'qa')
assert sha(bp)==a.base_sha256 and sha(gp)==a.repair_generation_sha256
assert not out.exists()
b=read(bp);g=read(gp);rpath=resolve(g['file'])
assert g['route']=='builtin' and g['nativePixelsResampled'] is False
assert [g['width'],g['height']]==[1254,1254] and sha(rpath)==g['sha256']
basepath=bp.parent/b['context']['path'];idpath=bp.parent/b['sourceIdMap']['path']
assert sha(basepath)==b['context']['sha256'] and sha(idpath)==b['sourceIdMap']['sha256']
base=image(basepath);ids=np.asarray(Image.open(idpath)).astype(np.uint16).copy();repair=image(rpath)
coords=g.get('coordinates',g);gb=coords['globalNativeBox'];origin=b['globalContextBox'][:2]
x,y=gb[0]-origin[0],gb[1]-origin[1]
assert gb[2]-gb[0]==1254 and gb[3]-gb[1]==1254
assert x < 0 and x+1254 > 0 and 0<=y and y+1254<=base.shape[0]
assert x+1254<=base.shape[1]
sx=-x;ex=1254;bx=0;br=x+1254
if a.open_bottom: assert y+1254==base.shape[0]
if a.open_top: assert y==0
if a.open_left: assert x==0
if a.open_right: assert x+1254==base.shape[1]
spec=importlib.util.spec_from_file_location('assembly_native',ROOT/'scripts/assembly-v4.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
request=read(g['request']['path'])
assert sha(g['request']['path'])==g['request']['sha256']
ref=request['references'][0]
assert sha(ref['path'])==ref['sha256']
old=image(ref['path'])
assert old.shape==(1254,1254,3)
assert np.array_equal(old[:,627:],base[y:y+1254,115:742])
left,lc=m.minimum_seam(old[:,:230],repair[:,:230])
right,rc=m.minimum_seam(old[:,1024:],repair[:,1024:]);right+=1024
top,tc=m.minimum_seam(old[:230].transpose(1,0,2),repair[:230].transpose(1,0,2))
bottom,bc=m.minimum_seam(old[1024:].transpose(1,0,2),repair[1024:].transpose(1,0,2));bottom+=1024
xx=np.arange(1254)[None,:];yy=np.arange(1254)[:,None]
take=np.ones((1254,1254),dtype=bool)
if not a.open_left: take &= xx>=left[:,None]
if not a.open_right: take &= xx<right[:,None]
if not a.open_top: take &= yy>=top[None,:]
if not a.open_bottom: take &= yy<bottom[None,:]
sid=max(1001,max(int(s['sourceId'])+1 for s in b['sourceLegend'] if int(s['sourceId'])!=65535))
assert sid<65535
take[:,:sx]=False
clippedTake=take[:,sx:ex]
base[y:y+1254,bx:br][clippedTake]=repair[:,sx:ex][clippedTake]
ids[y:y+1254,bx:br][clippedTake]=sid
source={'sourceId':sid,'path':rpath.relative_to(ROOT).as_posix(),'sha256':g['sha256'],'generationRecord':{'path':str(gp),'sha256':sha(gp)},'globalNativeBox':gb,'globalCoreBox':coords['globalCoreBox'],'dimensions':[1254,1254],'sourceKind':'generated-native-AI-seam-repair','actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'route':'builtin','nativePixelsResampled':False}
legend=b['sourceLegend']+[source];sources=[]
for item in legend:
    sp=resolve(item['path']);assert sha(sp)==item['sha256']
    sources.append({**item,'array':image(sp)})
proof=m.replay(base,ids,sources,origin)
assert sha(bp)==a.base_sha256 and sha(gp)==a.repair_generation_sha256 and sha(basepath)==b['context']['sha256']
out.mkdir(parents=True,exist_ok=False)
ctx=save(out/'context-native.png',base);imap=save(out/'source-id.png',ids)
save(out/'repair-source-mask.png',(take*255).astype(np.uint8))
local=save(out/'repair-overlay-native.png',base[y:y+1254,bx:br])
tiles=[]
for tile in b['tiles']:
    x0,y0,x1,y1=tile['contextCropBox'];ref=save(out/tile['path'],base[y0:y1,x0:x1]);ref.update({k:tile[k] for k in ('tile','contextCropBox','globalCoreBox')});ref.update(formalAccepted=False,internalQa='pending repair boundaries; prior other failures retained',externalQa='pending');tiles.append(ref)
record={k:v for k,v in b.items() if k not in ('context','sourceIdMap','sourceLegend','proof','qa','script','tiles')}
record.update(createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='native-AI-repair-overlay-pending-visual-QA',formalAccepted=False,context=ctx,sourceIdMap=imap,sourceLegend=legend,proof=proof,tiles=tiles)
record['script']={'path':str(Path(__file__).resolve()),'sha256':sha(__file__)}
record['baseAssembly']={'path':str(bp),'sha256':sha(bp)}
record['repairOverlay']={'sourceId':sid,'globalNativeBox':gb,'contextBox':[bx,y,br,y+1254],'fullRepairContextBox':[x,y,x+1254,y+1254],'clippedSourceBox':[sx,0,ex,1254],'selectedPixelCount':int(take.sum()),'method':'four native border paths, clipped to current C07 context; no external file writes; hard source selection','borderWidth':230,'leftPath':left.tolist(),'rightPath':right.tolist(),'topPath':top.tolist(),'bottomPath':None if a.open_bottom else bottom.tolist(),'openBottom':a.open_bottom,'openTop':a.open_top,'openLeft':a.open_left,'openRight':a.open_right,'blend':False,'resize':False,'paint':False,'sourceMask':{'path':'repair-source-mask.png','sha256':sha(out/'repair-source-mask.png')},'nativeReviewCrop':local}
record['qa']={'reviewed':False,'affectedContextBox':[bx,y,br,y+1254],'priorOtherFindingsRemainOpen':True,'external':'pending','note':'No prior visual failure is automatically cleared by pixel replay.'}
savej(out/'assembly.json',record)
print(json.dumps({'outputDirectory':str(out),'assemblySha256':sha(out/'assembly.json'),'repairSourceId':sid,'selectedRepairPixels':int(take.sum()),'sourceReplay':proof}))
