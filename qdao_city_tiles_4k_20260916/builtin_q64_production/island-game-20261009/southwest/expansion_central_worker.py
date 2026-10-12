"""Coordinate-safe native preparation and ingestion for central southern expansion."""
from production import *
import sys,re

INDEX=ROOT/'qa/expansion-central-worker-map.json'
ALLOWED={f'r{r:02}_c{c:02}' for r in range(11,15) for c in [3,4]}
def state():return load(INDEX) if INDEX.exists() else {'status':'generating','candidateArtifacts':{},'formalAccepted':False}
def prepare(r,c,sr,sc,v=1):
 co=coords(r,c,sr,sc);tile=co['tile'];assert tile in ALLOWED
 stem=f'{tile}_s{sr:02}_{sc:02}_v{v:02}';assert not (ROOT/'prompts'/f'{stem}.request.json').exists()
 box=co['nativeGlobalBox'];layout=ROOT/'guides'/f'{stem}.layout-only.png'
 with Image.open(REFS[0][0]) as im:im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(layout)
 dump(str(layout)+'.derivation.json',{'operation':'Bicubic overview EXTENT; layout-only, never final pixels','derivedFrom':metadata(*REFS[0]),'coordinates':co,'sha256':hashfile(layout)})
 canvas=Image.open(layout).convert('RGB');sources=[metadata(layout,'layout-only base')]
 indices=[load(ROOT/'current-native-map.json')]
 for p in (ROOT/'qa').glob('expansion-*-worker-map.json'):indices.append(load(p))
 selected={};artifacts={}
 for data in indices:
  for k,arr in data.items():
   if re.fullmatch(r'r\d{2}_c\d{2}',k) and isinstance(arr,list):
    for row in arr:
     for s in row:
      if s:selected[s]=True
  artifacts.update(data.get('candidateArtifacts',{}))
 def paste(p,b,role,extra=None):
  ib=[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]
  if ib[0]>=ib[2] or ib[1]>=ib[3]:return
  crop=[ib[0]-b[0],ib[1]-b[1],ib[2]-b[0],ib[3]-b[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
  with Image.open(p) as im:canvas.paste(im.crop(crop),dest)
  sources.append({**metadata(p,role),'sourceCrop':crop,'destinationTopLeft':dest,**(extra or {})})
 for s in selected:
  p=ROOT/'native'/f'{s}.png';rec=load(str(p)+'.generation.json');paste(p,rec['coordinates']['nativeGlobalBox'],'selected adjacent native same-coordinate overlap')
 for t,rec in artifacts.items():
  rr,cc=map(int,re.fullmatch(r'r(\d+)_c(\d+)',t).groups());b=[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096]
  paste(Path(rec['path']),b,'latest full4K candidate exact border; priority over raw sources',{'record':rec.get('record') or rec.get('report')})
 guide=ROOT/'guides'/f'{stem}.native-overlap-guide.png';canvas.save(guide)
 dump(str(guide)+'.derivation.json',{'operation':'same-global-coordinate native hard crop/paste over layout-only guide; no native resampling','coordinates':co,'sources':sources,'sha256':hashfile(guide)})
 dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
 refs=[metadata(guide,'fixed-coordinate edit target: sharp native neighbor pixels locked; blurry area requires native detail redraw')]+[metadata(*r) for r in REFS]
 dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None})
 print(json.dumps({'stem':stem,'guide':str(guide),'references':[x['path'] for x in refs],'coordinates':co}))
def ingest_local(stem,source):
 p=ROOT/'native'/f'{stem}.png';assert not p.exists();shutil.copy2(source,p)
 req=load(ROOT/'prompts'/f'{stem}.request.json');co=req['coordinates'];assert co['tile'] in ALLOWED
 with Image.open(p) as im:size=im.size;fmt=im.format
 assert size==(1254,1254)
 rec={'file':str(p),'sha256':hashfile(p),'generatedAt':now(),'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host does not expose verified actual model/quality','prompt':str(ROOT/'prompts'/f'{stem}.prompt.txt'),'references':req['references'],'sourceToolPath':str(source),'evidence':[{'path':str(ROOT/'receipts'/f'{stem}.tool.json'),'type':'tool receipt'}],'coordinates':co,'status':'awaiting_visual_QA','nativeSizeMatchesPlan':True}
 dump(str(p)+'.generation.json',rec);print(json.dumps({'path':str(p),'sha256':rec['sha256'],'dimensions':size}))
def select(stem,note):
 co=load(ROOT/'prompts'/f'{stem}.coordinates.json');d=state();a=d.setdefault(co['tile'],[[None]*4 for _ in range(4)]);a[co['subrow']-1][co['subcolumn']-1]=stem
 d.setdefault('qa',{})[stem]={'checkedAtUtc':now(),'note':note,'status':'native candidate; full tile/group review pending'};d['updatedAtUtc']=now();dump(INDEX,d)
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='prepare':prepare(*map(int,sys.argv[2:]))
 elif cmd=='ingest':ingest_local(*sys.argv[2:])
 elif cmd=='select':select(*sys.argv[2:])
