from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,shutil,re
from datetime import datetime,timezone
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r02_c02'
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009')
REFS=[P/'donghai-natural-stone-clear-routes-v10.png',P/'donghai-natural-stone-detail-v1.png',P/'user-references-20261009/mail-daoist-style.jpg']
E=B/'work-r02_c03/resume-20261012-v1/final-v2-verified';EF=B/'work-r02_c03/resume-20261012-v1/composition-v11'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,a):Path(p).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
for d in ['native','guides','receipts','prompts','qa','tiles']:(W/d).mkdir(parents=True,exist_ok=True)
def name(r,c,v=1):return f'r02_c02_s{r:02d}_s{c:02d}_v{v:02d}'
def box(r,c):
 x=4096+(c-1)*1024;y=4096+(r-1)*1024;return [x-115,y-115,x+1139,y+1139]
def native(r,c):
 m=read(W/'selection.json') if (W/'selection.json').exists() else {};p=Path(m.get(f'{r},{c}',{}).get('file',W/'native'/(name(r,c)+'.png')));return p if p.exists() else None
def southern_context():
 p=W/'guides/r03_c02-adopted-current-20261012.north-context.png'
 if p.exists():return p
 index=read(B/'current-artifacts.json');ap=B/index['r03_c02']['assembly'];m=read(ap);a=np.asarray(Image.open(m['candidate']['file']));ids=np.asarray(Image.open(m['sourceIdMap']['file']));s={str(z['sourceId']):z for z in m['sources']} if isinstance(m['sources'],list) else m['sources'];out=np.empty((1254,4326,3),dtype=np.uint8);gy,gx=np.indices(out.shape[:2]);gx+=3981;gy+=8077;oi=ids[np.clip(gy-8192,0,4095),np.clip(gx-4096,0,4095)]
 for k in np.unique(oi):
  z=s[str(k)];im=np.asarray(Image.open(z['file']));yy,xx=np.nonzero(oi==k);sx=gx[yy,xx]-z['globalNativeBox'][0];sy=gy[yy,xx]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)) and np.all((sy>=0)&(sy<1254));out[yy,xx]=im[sy,sx]
 inside=(gx>=4096)&(gx<8192)&(gy>=8192);assert np.array_equal(out[inside],a[(gy-8192)[inside],(gx-4096)[inside]])
 Image.fromarray(out).save(p);delta=read(E/'r03_c02.reviewed.delta.json');write(str(p)+'.derivation.json',{'globalBox':[3981,8077,8307,9331],'file':str(p),'sha256':sha(p),'sourceAssembly':str(ap),'sourceAssemblySha256':sha(ap),'sourceCandidate':m['candidate'],'independentDelta':{'file':str(E/'r03_c02.reviewed.delta.json'),'sha256':sha(E/'r03_c02.reviewed.delta.json')},'baseCandidate':delta['baseCandidate'],'corePixelsExactMismatches':0,'nativeScale':1,'topLeftRightHalo':'native coordinate continuation of source selected at nearest core edge; guide only','guideOnly':True})
 return p
def prepare(r,c,v=1):
 n=name(r,c,v);b=box(r,c);lay=Image.open(REFS[0]);fraction=[v*lay.width/57344 for v in b];im=lay.transform((1254,1254),Image.Transform.EXTENT,fraction,Image.Resampling.BICUBIC);neighbors=[]
 for rr,cc in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
  p=native(rr,cc) if 1<=rr<=4 and 1<=cc<=4 else None
  if p:
   nb=box(rr,cc);inter=[max(b[0],nb[0]),max(b[1],nb[1]),min(b[2],nb[2]),min(b[3],nb[3])]
   if inter[2]>inter[0] and inter[3]>inter[1]:
    crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-b[0],inter[1]-b[1]];im.paste(Image.open(p).crop(crop),dest);neighbors.append({'file':str(p),'sha256':sha(p),'crop':crop,'destination':dest,'role':'actual unscaled existing own native neighbor'})
 if r==4:
  p=southern_context();crop=[(c-1)*1024,0,(c-1)*1024+1254,230];im.paste(Image.open(p).crop(crop),(0,1024));neighbors.append({'file':str(p),'sha256':sha(p),'crop':crop,'destination':[0,1024],'role':'south neighbor with verified independent delta, exact native pixels; baseline/proposal hashes in derivation'})
 if c==4:
  p=EF/'full-pair.png';crop=[0,(r-1)*1024,230,(r-1)*1024+1254];im.paste(Image.open(p).crop(crop),(1024,0));neighbors.append({'file':str(p),'sha256':sha(p),'crop':crop,'destination':[1024,0],'role':'east neighbor r02_c03 final-v2-verified exact core plus current native left halo','candidate':{'file':str(E/'r02_c03.candidate.png'),'sha256':sha(E/'r02_c03.candidate.png')}})
 p=W/'guides'/(n+'.guide.png');assert not p.exists();im.save(p);write(str(p)+'.derivation.json',{'file':str(p),'sha256':sha(p),'globalNativeBox':b,'layout':{'file':str(REFS[0]),'sha256':sha(REFS[0]),'fractionalBox':fraction,'resamplingForGuideOnly':True},'neighbors':neighbors,'nativeOutputResampled':False,'guideOnly':True})
 write(W/'receipts'/(n+'.prepared.json'),{'name':n,'guide':str(p),'globalNativeBox':b,'neighbors':neighbors});print(json.dumps(read(W/'receipts'/(n+'.prepared.json')),ensure_ascii=False))
def request(r,c,v,prompt):
 n=name(r,c,v);g=W/'guides'/(n+'.guide.png');refs=[g]+REFS;roles=['EDIT TARGET: registered layout crop with actual native neighbor borders','REFERENCE: whole village layout only','REFERENCE: natural stone and architectural material detail only','PRIMARY REFERENCE: Q-style Daoist game painting'];pp=W/'prompts'/(n+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf8');write(W/'receipts'/(n+'.request.json'),{'requestedAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','globalNativeBox':box(r,c),'promptFile':str(pp),'prompt':prompt,'referenced_image_paths':[str(p).replace('\\','/') for p in refs],'referenceRoles':roles,'references':[{'file':str(p).replace('\\','/'),'sha256':sha(p),'role':role} for p,role in zip(refs,roles)],'guideDerivation':{'file':str(g)+'.derivation.json','sha256':sha(str(g)+'.derivation.json')},'transparent_background':False,'actualModel':None,'actualQuality':None,'modelQualityReason':'Built-in exposes no model/quality selectors or actual response metadata.'})
def save(n):
 req=read(W/'receipts'/(n+'.request.json'));rec=read(W/'receipts'/(n+'.receipt.json'));original=Path(re.search(r' as (C:\\[^\n]+?\.png) by default',rec['output_hint']).group(1));p=W/'native'/(n+'.png');assert not p.exists();shutil.copy2(original,p);im=Image.open(p);assert im.size==(1254,1254);assert im.mode in ['RGB','RGBA'];assert im.mode!='RGBA' or im.getextrema()[3]==(255,255);b=req['globalNativeBox']
 g={'file':str(p),'sha256':sha(p),'generatedAtUtc':rec['returnedAtUtc'],'width':1254,'height':1254,'format':'PNG','route':'builtin','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in exposes no model/quality selectors or actual response metadata.','globalNativeBox':b,'globalCoreBox':[b[0]+115,b[1]+115,b[2]-115,b[3]-115],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'evidence':{'receipt':str(W/'receipts'/(n+'.receipt.json')),'receiptSha256':sha(W/'receipts'/(n+'.receipt.json')),'request':str(W/'receipts'/(n+'.request.json')),'requestSha256':sha(W/'receipts'/(n+'.request.json'))},'prompt':str(W/'prompts'/(n+'.prompt.txt')),'promptSha256':sha(W/'prompts'/(n+'.prompt.txt')),'references':req['references'],'toolOriginal':{'file':str(original),'sha256':sha(original)},'status':'candidate-pending-full-join-review'};write(str(p)+'.generation.json',g);im.crop((115,115,1139,1139)).save(W/'qa'/(n+'.core.png'));selection=read(W/'selection.json') if (W/'selection.json').exists() else {};m=re.match(r'r02_c02_s(\d+)_s(\d+)_v\d+',n);selection[f'{int(m.group(1))},{int(m.group(2))}']={'file':str(p),'sha256':sha(p),'status':'raw-core-awaiting-assembly-review'};write(W/'selection.json',selection);print(json.dumps({'file':str(p),'sha256':sha(p),'dimensions':im.size}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]) if len(sys.argv)>4 else 1)
 elif sys.argv[1]=='save':save(sys.argv[2])
