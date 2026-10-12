"""Unscaled native cross-seam edit inputs and explicitly bounded adoption."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
from PIL import Image
T=Path(__file__).resolve().parent
Z=T.parent
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def coord(tile,pid):
 p=T/'coordinate-plan.json' if tile=='r10_c10' else Z/'coordinate-plan.json'
 return next(patch for patch in read(p)['patches'] if patch['id']==pid)
def source(tile,pid):
 if tile=='r10_c09':return Z/tile/'native'/'p14-v3.png'
 return T/read(T/'selected-patches.json')['patches'][pid]
J={'west':('r10_c09','p14','p11',36864),'p11-p12':('r10_c10','p11','p12',37888),'p13-p14':('r10_c10','p13','p14',39936),'p33-p34':('r10_c10','p33','p34',39936)}
mode,jid=sys.argv[1:3]
lefttile,lpid,rpid,seam=J[jid]
root=T/'joint'/jid
root.mkdir(parents=True,exist_ok=True)
if mode=='prepare':
 ybase=38797 if jid=='p33-p34' else 36749
 box=[seam-627,ybase,seam+627,ybase+1254]
 canvas=Image.new('RGB',(1254,1254));sources=[]
 for tile,pid,side,worldbox in [(lefttile,lpid,'left',[box[0],box[1],seam,box[3]]),('r10_c10',rpid,'right',[seam,box[1],box[2],box[3]])]:
  p=source(tile,pid);native=Image.open(p);assert native.size==(1254,1254)
  c=coord(tile,pid)['globalBox'];crop=[worldbox[0]-c[0],worldbox[1]-c[1],worldbox[2]-c[0],worldbox[3]-c[1]];at=[worldbox[0]-box[0],worldbox[1]-box[1]]
  canvas.paste(native.crop(crop),tuple(at));sources.append({'tile':tile,'patch':pid,'path':str(p),'sha256':sha(p),'globalBox':c,'sourceCrop':crop,'destination':at,'contributedWorldBox':worldbox})
 out=root/'joint-input-native-1254.png';canvas.save(out)
 record={'file':str(out),'sha256':sha(out),'dimensions':[1254,1254],'globalBox':box,'seamX':627,'coreSeamGlobalX':seam,'operation':'unscaled native crops joined at core boundary; no layout pixels','sources':sources,'createdAt':now(),'status':'edit input only'}
 write(out.with_suffix('.png.derivation.json'),record);print(json.dumps(record,indent=2))
elif mode=='ingest':
 version,src=sys.argv[3:5];stem='repair-'+version;dest=root/(stem+'.png');assert not dest.exists();shutil.copy2(src,dest)
 image=Image.open(dest);req=read(root/(stem+'.request.json'));receipt=read(root/(stem+'.receipt.json'));input_record=read(root/'joint-input-native-1254.png.derivation.json')
 refs=[{'path':p,'sha256':sha(p),'role':req['referenceRoles'][str(i+1)]} for i,p in enumerate(req['referenced_image_paths'])]
 record={'file':str(dest),'sha256':sha(dest),'generatedAt':receipt['receivedAt'],'generatedAtBasis':'tool response receipt captured','width':image.width,'height':image.height,'nativeDimensions':list(image.size),'format':image.format,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':read(Z.parents[3]/'config'/'image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin; model and quality selectors and actual metadata undisclosed','prompt':str(root/(stem+'.prompt.txt')),'references':refs,'evidence':{'receipt':str(root/(stem+'.receipt.json')),'sourcePath':src},'coordinate':{'globalBox':input_record['globalBox'],'seamX':627},'status':'candidate_pending_bounded_adoption_QA','upsamplingApplied':False}
 write(dest.with_suffix('.png.generation.json'),record);assert image.size==(1254,1254),'Do not resize unexpected native result';print(json.dumps({'file':str(dest),'dimensions':list(image.size)},indent=2))
elif mode=='adopt':
 version=sys.argv[3];adopt=list(map(int,sys.argv[4:8]));assert len(adopt)==4
 repair=root/('repair-'+version+'.png');im=Image.open(repair);assert im.size==(1254,1254)
 input_rec=read(root/'joint-input-native-1254.png.derivation.json');gb=input_rec['globalBox'];world=[gb[0]+adopt[0],gb[1]+adopt[1],gb[0]+adopt[2],gb[1]+adopt[3]]
 assert world[0]>=36864,'Cannot modify west tile; restrict adoption to r10_c10'
 selection=read(T/'selected-patches.json');outputs=[]
 for pid in list(selection['patches']):
  pb=coord('r10_c10',pid)['globalBox'];b=[max(pb[0],world[0]),max(pb[1],world[1]),min(pb[2],world[2]),min(pb[3],world[3])]
  if b[0]>=b[2] or b[1]>=b[3]:continue
  base=T/selection['patches'][pid];canvas=Image.open(base).copy();crop=[b[0]-gb[0],b[1]-gb[1],b[2]-gb[0],b[3]-gb[1]];at=[b[0]-pb[0],b[1]-pb[1]]
  canvas.paste(im.crop(crop),tuple(at));out=T/'processed'/f'{pid}-joint-{jid}-{version}.png';out.parent.mkdir(exist_ok=True);canvas.save(out)
  record={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'operation':'unscaled rectangular replacement from AI-edited native cross-seam patch; all other pixels preserved','base':{'path':str(base),'sha256':sha(base)},'repairSource':{'path':str(repair),'sha256':sha(repair),'generationRecord':str(repair.with_suffix('.png.generation.json'))},'repairGlobalBox':gb,'adoptedWorldBox':b,'repairCrop':crop,'destination':at,'adoptionRectInRepair':adopt,'createdAt':now(),'resamplingApplied':False,'status':'candidate_requires_join_QA'}
  write(out.with_suffix('.png.derivation.json'),record);selection['patches'][pid]=out.relative_to(T).as_posix();outputs.append(str(out))
 write(T/'selected-patches.json',selection);print(json.dumps({'adoptedWorldBox':world,'outputs':outputs},indent=2))
