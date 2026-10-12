import sys,json,hashlib,importlib.util
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
sys.dont_write_bytecode=True
Z=Path(__file__).resolve().parent.parent;N=Z/'native';L=Z/'layout-only';Q=Z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mode=sys.argv[1];tile='r09_c03'
if mode=='prepare':
 patch=sys.argv[2];version=sys.argv[3] if len(sys.argv)>3 else 'v1';stem=tile+'_'+patch+'_'+version
 p=next(t for t in read(Z/'coordinate-plan.json')['tiles'] if t['tile']==tile);coord=next(x for x in p['patches'] if x['id']==patch);box=coord['globalContextBox']
 refs=read(Z/'references.json');im=Image.open(refs[0]['path'])
 for name,gb in [(tile,p['globalCoreBox']),(tile+'_'+patch,box)]:
  out=L/(name+'.png');bbox=[v*1254/57344 for v in gb]
  if not out.exists():im.transform((1254,1254),Image.Transform.EXTENT,bbox,resample=Image.Resampling.NEAREST).save(out)
  write(Path(str(out)+'.derivation.json'),{'source':refs[0],'globalBox':gb,'sourceBoxFloat':bbox,'operation':'nearest-neighbor enlarged layout guide only, NEVER final pixels','file':out.as_posix(),'sha256':sha(out)})
 canvas=Image.open(L/(tile+'_'+patch+'.png')).convert('RGB');sources=[];selected={}
 for rp in sorted(N.glob(tile+'_p*.png.generation.json')):
  r=read(rp)
  if r.get('status') in ['rejected','superseded']:continue
  key=r['coordinates']['id'];v=int(rp.name.split('_v')[1].split('.')[0])
  if key not in selected or v>selected[key][0]:selected[key]=(v,r)
 for _,r in selected.values():
  b=r['coordinates']['globalContextBox'];inter=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
  if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
  if inter[2]-inter[0]>230 and inter[3]-inter[1]>230:continue
  crop=Image.open(r['file']).crop((inter[0]-b[0],inter[1]-b[1],inter[2]-b[0],inter[3]-b[1]));dst=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]];canvas.paste(crop,tuple(dst[:2]));sources.append({'path':r['file'],'sha256':r['sha256'],'globalOverlapBox':inter,'targetBox':dst,'role':'same-tile native overlap; preserve'})
 anchor=Q/'r09c03-r09c04-east-anchor-native.png';b=[12173,32653,16499,36979];inter=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
 if inter[0]<inter[2] and inter[1]<inter[3]:
  crop=Image.open(anchor).crop((inter[0]-b[0],inter[1]-b[1],inter[2]-b[0],inter[3]-b[1]));dst=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]];canvas.paste(crop,tuple(dst[:2]));sources.append({'path':anchor.as_posix(),'sha256':sha(anchor),'globalOverlapBox':inter,'targetBox':dst,'role':'latest accepted east neighbor topJoint left4326; highest-priority geometry and material anchor'})
 out=L/(stem+'_continuity.png');canvas.save(out);write(Path(str(out)+'.derivation.json'),{'file':out.as_posix(),'sha256':sha(out),'role':'guide only: native overlaps plus low-resolution layout placeholder','nativeSources':sources,'noNativeResample':True})
 rr=[{'path':out.as_posix(),'sha256':sha(out),'role':'exact coordinate edit target: replace coarse pixels with native detailed drawing; preserve sharp native overlap bands'},refs[1],refs[2],{'path':(L/(tile+'.png')).as_posix(),'sha256':sha(L/(tile+'.png')),'role':'whole tile LAYOUT ONLY: spatial context, do not render whole tile'}]
 req={'stem':stem,'tile':tile,'patch':patch,'coordinates':coord,'references':rr,'overlaps':sources,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'preparedAtUtc':datetime.now(timezone.utc).isoformat()}
 write(N/(stem+'.request.json'),req);print(json.dumps({'stem':stem,'refs':[r['path'] for r in rr],'overlaps':sources}))
elif mode=='record':
 stem=sys.argv[2];p=N/(stem+'.png');r=read(N/(stem+'.request.json'));receipt=read(N/(stem+'.receipt.json'));im=Image.open(p);assert im.size==(1254,1254)
 for x in r['references']:assert sha(x['path'])==x['sha256']
 rec={**r,'file':p.as_posix(),'sha256':sha(p),'width':1254,'height':1254,'dimensions':[1254,1254],'format':im.format,'route':'builtin','tool':'image_gen__imagegen','generatedAt':receipt['finishedAtUtc'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool has no model/quality selectors and returns no actual version evidence','prompt':(N/(stem+'.prompt.txt')).as_posix(),'receipt':(N/(stem+'.receipt.json')).as_posix(),'status':'candidate_pending_seam_qa','nativePixelsResampled':False}
 write(Path(str(p)+'.generation.json'),rec);print(json.dumps({'file':rec['file'],'sha256':rec['sha256'],'dimensions':[1254,1254]}))

