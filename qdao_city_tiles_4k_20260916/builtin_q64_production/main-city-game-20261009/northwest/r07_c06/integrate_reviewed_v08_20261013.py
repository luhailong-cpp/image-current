from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z));import assemble_native as A
def rd(f):return json.loads(Path(f).read_text(encoding='utf-8'))
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()}
def wj(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prev=T/'candidate/native-overlays-20261012-v07.json';r=rd(prev);pix=np.array(Image.open(r['candidate']['file']).convert('RGB'));own=np.array(Image.open(r['sourceIndex']['file']));src=list(r['nativeSources']);overlays=list(r['overlays'])
S=Z/'r07_c05/bridges/shared-east-lower-02';D=T/'repair-batches/c4-upper-material-01';Q=T/'qa/restart-integration-20261013'
new=[('shared-east-lower-02',S,[627,473,678,596],[0,2673,51,2796],[-627,2200],S/'generation.json',Q/'shared-lower-independent-review.json'),('c4-upper-material-01',D,[115,571,1254,700],[2957,853,4096,982],[2842,282],D/'generation-recovered-after-interruption.json',Q/'c4-upper-independent-review.json')]
for name,folder,sr,tr,origin,gr,review in new:
 f=folder/'native.png';n=np.array(Image.open(f).convert('RGB'));a,b,c,d=sr;x,y,x2,y2=tr;assert [a+origin[0],b+origin[1],c+origin[0],d+origin[1]]==tr
 pix[y:y2,x:x2]=n[b:d,a:c];own[y:y2,x:x2]=len(src);g=rd(gr);assert ref(g['sourceHostFile'])['sha256']==ref(f)['sha256'];world=[20480+origin[0],24576+origin[1],20480+origin[0]+1254,24576+origin[1]+1254]
 s={'id':name,**ref(f),'tileOriginXY':origin,'worldBox':world,'generationRecord':ref(gr),'sourceROI':sr,'tileROI':tr,'hostOutputFile':g['sourceHostFile'],'localReview':ref(review)};src.append(s);overlays.append({'id':name,**ref(f),'nativeWorldBox':world,'sourceROI':sr,'candidateROI':tr,'generationRecord':ref(gr),'localReview':ref(review)})
proof=[]
for i,s in enumerate(src):
 f=Path(s['file']);assert ref(f)['sha256']==s['sha256'];n=np.array(Image.open(f).convert('RGB'));ys,xs=np.where(own==i);ox,oy=s['tileOriginXY'];assert np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]);assert ref(s['hostOutputFile'])['sha256']==s['sha256'];proof.append({'sourceIndex':i,'pixelCount':len(xs),'exactSameWorldNativePixels':True,'hostByteIdentical':True})
assert sum(p['pixelCount'] for p in proof)==16777216
out=T/'candidate/r07_c06-candidate-native-roi-v08.png';Image.fromarray(pix).save(out);owner=T/'candidate/r07_c06-candidate-native-roi-v08-source-index.png';Image.fromarray(own).save(owner)
qaD=T/'qa/current-v08-native-20261013';qa=A.write_qa(Image.fromarray(pix),ref(out),qaD/'internal')
registry={'schemaVersion':2,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c06','candidate':ref(out),'sourceIndex':ref(owner),'nativeSources':src,'overlays':overlays,'previousRegistry':ref(prev),'pixelProof':{'status':'passed','checkedPixels':16777216,'sources':proof},'internalQa':qa,'status':'partial_repairs_integrated_pending_remaining_defects','internalPassed':False,'formalAccepted':False,'remainingDefects':['West cap material rectangle','Upper c3-c4 grout gap tile x3072 y572..632','Other actual west grout closures owned by root'],'sourceResampled':False,'blended':False,'recolored':False}
wj(T/'candidate/native-overlays-20261013-v08.json',registry)
# Pure native-pixel trial expanding the saved cap source to include the still-unrepaired row boundary at tile y1024.
B=T/'repair-batches/west-cap-material-01';trial=Image.fromarray(pix);n=Image.open(B/'native.png');sr=[200,455,450,680];tr=[0,967,250,1192];trial.paste(n.crop(sr),tr[:2]);trial.save(B/'trial-expanded-cap-4096.png');w=Image.open(Z/'r07_c05/candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/candidate.png');detail=Image.new('RGB',(550,420));detail.paste(w.crop((3976,900,4096,1320)),(0,0));detail.paste(trial.crop((0,900,430,1320)),(120,0));detail.save(B/'trial-expanded-cap-detail.png');wj(B/'trial-expanded-cap.json',{'candidate':ref(B/'trial-expanded-cap-4096.png'),'base':ref(out),'source':ref(B/'native.png'),'sourceROI':sr,'tileROI':tr,'status':'pending_review','formalAccepted':False})
print(json.dumps({'candidate':ref(out),'sources':len(src),'pixelsProven':16777216}))
