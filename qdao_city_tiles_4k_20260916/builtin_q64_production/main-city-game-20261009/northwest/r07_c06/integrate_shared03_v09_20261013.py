from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z));import assemble_native as A
def rd(f):return json.loads(Path(f).read_text(encoding='utf-8'))
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()}
def wj(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prev=T/'candidate/native-overlays-20261013-v08.json';r=rd(prev);pix=np.array(Image.open(r['candidate']['file']).convert('RGB'));own=np.array(Image.open(r['sourceIndex']['file']));src=list(r['nativeSources']);S=Z/'r07_c05/bridges/shared-east-lower-03';f=S/'native.png';g=rd(S/'generation.json');n=np.array(Image.open(f));sr=[627,795,657,910];tr=[0,2995,30,3110];pix[2995:3110,0:30]=n[795:910,627:657];own[2995:3110,0:30]=len(src)
s={'id':'shared-east-lower-03-bottom',**ref(f),'tileOriginXY':[-627,2200],'worldBox':[19853,26776,21107,28030],'generationRecord':ref(S/'generation.json'),'sourceROI':sr,'tileROI':tr,'hostOutputFile':g['sourceHostFile'],'localReview':ref(T/'qa/restart-integration-20261013/shared-bottom-independent-review.json')};src.append(s)
proof=[]
for i,s in enumerate(src):
 f=Path(s['file']);assert ref(f)['sha256']==s['sha256'];n=np.array(Image.open(f));ys,xs=np.where(own==i);ox,oy=s['tileOriginXY'];assert np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]);assert ref(s['hostOutputFile'])['sha256']==s['sha256'];proof.append({'sourceIndex':i,'pixelCount':len(xs),'exactSameWorldNativePixels':True,'hostByteIdentical':True})
out=T/'candidate/r07_c06-candidate-native-roi-v09.png';Image.fromarray(pix).save(out);owner=T/'candidate/r07_c06-candidate-native-roi-v09-source-index.png';Image.fromarray(own).save(owner);Q=T/'qa/current-v09-native-20261013';qa=A.write_qa(Image.fromarray(pix),ref(out),Q/'internal')
reg={**r,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':ref(out),'sourceIndex':ref(owner),'nativeSources':src,'previousRegistry':ref(prev),'pixelProof':{'status':'passed','checkedPixels':16777216,'sources':proof},'internalQa':qa,'status':'partial_repair_candidate_pending_remaining_defects'};reg['overlays']=r['overlays']+[{'id':'shared-east-lower-03-bottom',**ref(S/'native.png'),'nativeWorldBox':[19853,26776,21107,28030],'sourceROI':sr,'candidateROI':tr,'generationRecord':ref(S/'generation.json'),'localReview':s['localReview']}];wj(T/'candidate/native-overlays-20261013-v09.json',reg)
W=S/'r07_c05-combined-shared-proposal-4096.png';w=Image.open(W).convert('RGB');band=Image.new('RGB',(640,4096));band.paste(w.crop((3776,0,4096,4096)),(0,0));band.paste(Image.fromarray(pix).crop((0,0,320,4096)),(320,0));ext=[]
for i in range(4):
 f=Q/f'west-segment{i+1:02}.png';band.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90).save(f);ext.append(ref(f))
for i in range(1,4):
 f=Q/f'west-junction-{i*1024}.png';band.crop((160,i*1024-160,480,i*1024+160)).save(f);ext.append(ref(f))
wj(Q/'actual-west-inputs.json',{'west':ref(W),'candidate':ref(out),'crops':ext,'pixelScale':1})
wj(T/'repair-batches/west-cap-material-02/review.json',{'actuallyViewed':[ref(T/'repair-batches/west-cap-material-02/trial-expanded-cap-detail.png')],'verdict':'needs_repair_not_adopted','finding':'Second native attempt retains large rectangular material corner against actual west at tile y1024 and x0. Triangle stays closed, but material remains unaccepted.','consecutiveAttemptsWithoutResolution':2,'next':'deferred while independent defect work continues','formalAccepted':False})
print(json.dumps({'candidate':ref(out),'registry':ref(T/'candidate/native-overlays-20261013-v09.json'),'nativeSources':len(src)}))
