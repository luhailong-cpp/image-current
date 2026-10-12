"""Persist one p22/p23 image_gen bridge and mechanical candidates/QA only."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib,shutil,datetime,re
Z=Path(__file__).resolve().parent.parent
P='r06_c12_p22-p23-bridge'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
 p=Path(p)
 if p.exists():raise ValueError(f'Refusing to replace {p}')
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):return {'path':str(p),'sha256':sha(p),'role':role}
def openim(p):
 im=Image.open(p);im.load()
 if im.size!=(1254,1254):raise ValueError(f'Bad native dimensions {p}')
 return im.convert('RGB')
rp=Z/'records'/f'{P}-v1.receipt.json';receipt=read(rp)
source=Path(re.search(r' as (.+?) by default\.',receipt['response']['output_hint']).group(1))
native=Z/'native'/f'{P}-v1.png'
if native.exists():raise ValueError('Bridge native already exists')
shutil.copy2(source,native)
if sha(native)!=sha(source):raise ValueError('Copy hash mismatch')
im=openim(native)
prompt=Z/'records'/f'{P}-v1.prompt.txt'
target=Z/'guides'/f'{P}-edit-target.png'
roles=['authoritative full-map layout only','independent material/close-up style only','primary approved Q Daoist hand-painted style, no UI/night copied','1:1 native p22/p23 seam edit target']
references=[]
for path,role in zip(receipt['request']['referenced_image_paths'],roles):
 p=Path(path);references.append(ref(p,role))
 side=Path(str(p)+'.derived.json')
 if side.exists():references[-1]['provenanceRecord']=ref(side,'mechanical target provenance')
record={'schemaVersion':1,'file':str(native),'sha256':sha(native),'width':1254,'height':1254,'format':'PNG',
 'nativeSize':[1254,1254],'generatedAt':None,'observedAtUtc':receipt['observedAtUtc'],
 'timeEvidence':'Exact generation time undisclosed; observedAtUtc is tool return observation',
 'nativeGlobalBox':[46477,21389,47731,22643],'tool':'image_gen.imagegen','route':'builtin',
 'configSnapshot':read(Z/'records'/f'{P}-config-snapshot.json'),'configSnapshotCaptureStage':'before_generation',
 'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,
 'unverifiedReason':'Host-managed; image_gen exposes no model/quality selectors and returns no actual model/quality metadata',
 'prompt':ref(prompt,'complete submitted prompt'),'receipt':ref(rp,'actual tool receipt without base64'),
 'references':references,'evidence':{'receipt':str(rp),'nativeMetadataKeys':list(Image.open(native).info)},
 'source':ref(source,'byte-for-byte copy; no resize'),'status':'candidate_pending_four_side_QA',
 'nativeResizePerformed':False,'formalAccepted':False,'usableNative':False}
save(str(native)+'.generation.json',record)
a=Z/'native/r06_c12_p22-v2.png';b=Z/'native/r06_c12_p23-v1.png'
ia,ib=openim(a),openim(b)
joined=Image.new('RGB',(2278,1254))
joined.paste(ia.crop((0,0,512,1254)),(0,0))
joined.paste(im,(512,0))
joined.paste(ib.crop((742,0,1254,1254)),(1766,0))
sources=[{**ref(p,'native pixel source'),'generationRecord':str(p)+'.generation.json'} for p in [a,native,b]]
candidates=[]
for patch,box,globalbox in [('p22',[0,0,1254,1254],[45965,21389,47219,22643]),('p23',[1024,0,2278,1254],[46989,21389,48243,22643])]:
 dest=Z/'native'/f'{P}-{patch}-candidate.png'
 if dest.exists():raise ValueError('Candidate already exists')
 joined.crop(box).save(dest)
 data={'file':str(dest),'sha256':sha(dest),'patchId':f'r06_c12_{patch}','pixels':[1254,1254],
  'nativeGlobalBox':globalbox,'derivedFrom':sources,'operation':'1:1 native crop and opaque paste only; no resize, blend or feather',
  'bridgeReplacementGlobalBox':[46477,21389,47731,22643],'combinedNativeGlobalBox':[45965,21389,48243,22643],
  'cropFromCombined':box,'sourcePlacements':[{'path':str(a),'sourceBox':[0,0,512,1254],'targetBox':[0,0,512,1254]},
   {'path':str(native),'sourceBox':[0,0,1254,1254],'targetBox':[512,0,1766,1254]},
   {'path':str(b),'sourceBox':[742,0,1254,1254],'targetBox':[1766,0,2278,1254]}],
  'status':'candidate_pending_four_side_QA','formalAccepted':False}
 save(str(dest)+'.derived.json',data);candidates.append(ref(dest,patch+' mechanically derived candidate'))
qa=[]
def saveqa(label,out,details,parents):
 dest=Z/'qa'/f'{P}-{label}.png'
 if dest.exists():raise ValueError('QA image already exists')
 out.save(dest)
 data={'file':str(dest),'sha256':sha(dest),'pixels':list(out.size),'pixelScale':1,
  'operation':'native 1:1 crop/opaque paste for QA, no resize, blend or painting','derivedFrom':parents,
  'visualReview':'pending','formalAccepted':False,**details}
 save(str(dest)+'.derived.json',data);qa.append(data)
for label,x in [('left-outer',512),('right-outer',1766),('core-seam',1139)]:
 box=[x-128,0,x+128,1254]
 saveqa(label,joined.crop(box),{'boxInCombined':box,'seamLocalX':128},sources)
def rowpair(left,right):
 l,r=openim(left),openim(right)
 out=Image.new('RGB',(2278,1254))
 out.paste(l.crop((0,0,1139,1254)),(0,0))
 out.paste(r.crop((115,0,1254,1254)),(1139,0))
 return out
above=[Z/'native/r06_c12_p12-bridge-candidate.png',Z/'native/r06_c12_p13-v2.png']
below=[Z/'native/r06_c12_p32-v1.png',Z/'native/r06_c12_p33-v1.png']
for label,paths in [('top-outer',above),('bottom-outer',below)]:
 other=rowpair(*paths)
 out=Image.new('RGB',(1254,256))
 if label=='top-outer':
  out.paste(other.crop((512,1011,1766,1139)),(0,0))
  out.paste(joined.crop((512,115,1766,243)),(0,128))
  boxes={'aboveCombinedBox':[512,1011,1766,1139],'candidateCombinedBox':[512,115,1766,243]}
 else:
  out.paste(joined.crop((512,1011,1766,1139)),(0,0))
  out.paste(other.crop((512,115,1766,243)),(0,128))
  boxes={'candidateCombinedBox':[512,1011,1766,1139],'belowCombinedBox':[512,115,1766,243]}
 saveqa(label,out,{'seamLocalY':128,'coverage':'entire1254 bridge width at adjacent row core boundary',**boxes},
  sources+[ref(p,label+' neighboring native source') for p in paths])
metrics={}
before=openim(target)
for side,box in [('left180',[0,0,180,1254]),('right180',[1074,0,1254,1254]),('top180',[0,0,1254,180]),('bottom180',[0,1074,1254,1254])]:
 d=ImageChops.difference(im.crop(box),before.crop(box))
 metrics[side]={'rgbMeanAbsoluteDifference':ImageStat.Stat(d).mean,'exactEqual':d.getbbox() is None,'allPixelsCompared':True,'box':box}
save(Z/'qa'/f'{P}-check.json',{'generatedNativeCountAdded':1,'derivedCandidateCount':2,'candidateFiles':candidates,
 'nativeBridge':ref(native,'one new builtin image_gen output'),'qa':qa,'outer180PixelMetrics':metrics,
 'visualReview':'pending; pixel differences alone are not geometry acceptance','formalAccepted':False,
 'strictComplete':False,'complete4kCountAdded':0,'progressModified':False,
 'filenameNote':'Both candidates retain the assigned p22-p23-bridge prefix; actual patch identity is in derived metadata. Parent may create traceable canonical aliases if chosen.'})
print(json.dumps({'nativeBridge':str(native),'candidates':candidates,'outer180PixelMetrics':metrics},ensure_ascii=False))

