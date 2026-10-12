from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,gc
from PIL import Image
ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southeast'
OUT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
progress=read(BASE/'progress.json')
adopted={x['tile']:Path(x['candidate']) for x in progress['currentAdoptedCandidates']}
groups=[('g01-r09-r10-c12-c13',9,12),('g02-r11-r12-c11-c12',11,11)]
allgroups=[]
for name,r,c in groups:
 q=OUT/name;q.mkdir(exist_ok=True)
 inputs=[];art=Image.new('RGB',(8192,8192))
 for rr in range(r,r+2):
  for cc in range(c,c+2):
   t=f'r{rr:02d}_c{cc:02d}';p=adopted[t]
   with Image.open(p) as im:
    assert im.size==(4096,4096);art.paste(im,((cc-c)*4096,(rr-r)*4096))
   inputs.append({'tileId':t,'file':str(p),'sha256':sha(p),'dimensions':[4096,4096],'groupOrigin':[(cc-c)*4096,(rr-r)*4096]})
 target=q/'native-hard-assembly-8192x8192-v01.png';art.save(target,compress_level=2)
 preview=q/'PREVIEW-downsampled-1024-NOT-native-v01.png';art.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
 cuts=[]
 for axis in ['vertical','horizontal']:
  for i in range(8):
   box=[3840,i*1024,4352,(i+1)*1024] if axis=='vertical' else [i*1024,3840,(i+1)*1024,4352]
   p=q/f'{axis}-{i+1:02d}-100pct.png';art.crop(box).save(p)
   cuts.append({'id':f'{axis}-{i+1:02d}','file':str(p),'sha256':sha(p),'groupSourceBox':box,'resampled':False,'visualStatus':'pending_current_review'})
  for j in range(2):
   block=cuts[-8+j*4:-8+(j+1)*4] if j==0 else cuts[-4:]
   if j==0:block=cuts[-8:-4]
   size=(1024,2048) if axis=='vertical' else (2048,1024)
   panel=Image.new('RGB',size)
   for k,z in enumerate(block):
    with Image.open(z['file']) as im:panel.paste(im,((k%2)*im.width,(k//2)*im.height))
   p=q/f'contact-{axis}-{j+1}-100pct-NO-resample.png';panel.save(p)
   cuts.append({'id':f'contact-{axis}-{j+1}','file':str(p),'sha256':sha(p),'resampled':False,'displayOrder':[z['id'] for z in block],'visualStatus':'pending_current_review'})
   panel.close()
 p=q/'four-tile-junction-100pct.png';box=[3584,3584,4608,4608];art.crop(box).save(p)
 cuts.append({'id':'four-tile-junction','file':str(p),'sha256':sha(p),'groupSourceBox':box,'resampled':False,'visualStatus':'pending_current_review'})
 # A source change makes the whole independent group stale.
 changed=[x['file'] for x in inputs if sha(x['file'])!=x['sha256']]
 d={'groupId':name,'tileCount':4,'inputs':inputs,'nativeAssembly':{'file':str(target),'sha256':sha(target),'dimensions':[8192,8192],'nativePixels':True,'operation':'integer whole-tile hard paste, no resize/blend/fill'},
    'preview':{'file':str(preview),'dimensions':[1024,1024],'nativePixels':False,'label':'PREVIEW ONLY'},
    'crops':cuts,'sourceChangedAfterExport':changed,'stale':bool(changed),'formalAccepted':False,'status':'mechanical_assembly_pending_seam_visual_review'}
 save(q/'manifest.json',d);allgroups.append(d);art.close();gc.collect();print('exported',name,flush=True)

# Four-way junction across incomplete r13_c11: use only its actually selected p14 core.
q=OUT/'breakpoints';q.mkdir(exist_ok=True)
sources=[adopted['r12_c11'],adopted['r12_c12'],BASE/'native/r13_c11_p14_v01.png',adopted['r13_c12']]
boxes=[[3584,3584,4096,4096],[0,3584,512,4096],[627,115,1139,627],[0,0,512,512]]
art=Image.new('RGB',(1024,1024));trace=[]
for k,(p,box) in enumerate(zip(sources,boxes)):
 with Image.open(p) as im:art.paste(im.crop(box),((k%2)*512,(k//2)*512))
 trace.append({'file':str(p),'sha256':sha(p),'sourceCrop':box,'destination':[(k%2)*512,(k//2)*512]})
p=q/'r12-r13-c11-c12-selected-core-junction-100pct.png';art.save(p)
targets=[{'id':'fourway-shared-column-current-selection','file':str(p),'sha256':sha(p),'sources':trace,'visualStatus':'pending','note':'r13_c11 is incomplete; this crop uses its selected p14, without silently adopting saved shared-lower proposal.'}]
pending=Path(progress['pendingCandidates'][0]['candidate'])
for ident,box in [('r12_c13-floor-groove-x1024-y2167',[640,1783,1408,2551]),('r12_c13-low-sail-batten-x3072-y3730',[2688,3328,3456,4096])]:
 p=q/(ident+'-100pct.png')
 with Image.open(pending) as im:im.crop(box).save(p)
 targets.append({'id':ident,'file':str(p),'sha256':sha(p),'sources':[{'file':str(pending),'sha256':sha(pending),'sourceCrop':box}],'visualStatus':'pending'})
save(q/'manifest.json',{'breakpoints':targets,'formalAccepted':False,'resampled':False})
save(OUT/'output-groups.json',{'groups':[{'groupId':g['groupId'],'manifest':str(OUT/g['groupId']/'manifest.json')} for g in allgroups],'breakpoints':str(q/'manifest.json'),'createdAtUtc':datetime.now(timezone.utc).isoformat()})
