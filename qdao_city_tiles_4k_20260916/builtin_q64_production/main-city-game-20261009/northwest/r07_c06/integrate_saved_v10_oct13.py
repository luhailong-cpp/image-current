from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z));import assemble_native as A
D=T/'qa/restart-saved-integration-20261013'
def rd(f):return json.loads(Path(f).read_text(encoding='utf-8'))
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()}
def wj(f,v):
    assert not f.exists(),str(f)
    f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prev=T/'candidate/native-overlays-20261013-v09.json';r=rd(prev)
pix=np.array(Image.open(r['candidate']['file']).convert('RGB'));own=np.array(Image.open(r['sourceIndex']['file']));src=list(r['nativeSources']);overlays=list(r['overlays'])
review=D/'local-saved-independent-review.json';assert review.exists()
# Two disjoint tiny ROIs from the same unchanged source; r07_c05's half is proposed separately.
M=T/'repair-batches/shared-west-micro-01';g=rd(M/'generation.json');n=np.array(Image.open(M/'native.png').convert('RGB'))
srlist=[[627,382,639,408],[627,1077,639,1103]]
for a,b,c,d in srlist:
    pix[b+2200:d+2200,a-627:c-627]=n[b:d,a:c];own[b+2200:d+2200,a-627:c-627]=len(src)
src.append({'id':'shared-west-micro-01-right',**ref(M/'native.png'),'tileOriginXY':[-627,2200],'worldBox':[19853,26776,21107,28030],'sourceROIs':srlist,'generationRecord':ref(M/'generation.json'),'hostOutputFile':g['sourceHostFile'],'localReview':ref(review)})
overlays.append({'id':'shared-west-micro-01-right',**ref(M/'native.png'),'sourceROIs':srlist,'tileOriginXY':[-627,2200],'localReview':ref(review)})
# Connector uses only 1,014 source-native pixels selected by the reviewed binary mask.
G=T/'repair-batches/c3c4-upper-gap-02';g=rd(G/'generation.json');n=np.array(Image.open(G/'native.png').convert('RGB'));mask=np.array(Image.open(D/'c3c4-narrow-mask.png'))>0;ys,xs=np.where(mask)
pix[ys,xs+2445]=n[ys,xs];own[ys,xs+2445]=len(src)
src.append({'id':'c3c4-upper-gap-02-narrow',**ref(G/'native.png'),'tileOriginXY':[2445,0],'worldBox':[22925,24576,24179,25830],'selectionMask':ref(D/'c3c4-narrow-mask.png'),'generationRecord':ref(G/'generation.json'),'hostOutputFile':g['sourceHostFile'],'localReview':ref(review),'remainingMaterialSeam':True})
overlays.append({'id':'c3c4-upper-gap-02-narrow',**ref(G/'native.png'),'selectionMask':ref(D/'c3c4-narrow-mask.png'),'tileOriginXY':[2445,0],'localReview':ref(review)})
proof=[]
for i,s in enumerate(src):
    f=Path(s['file']);assert ref(f)['sha256']==s['sha256'];n=np.array(Image.open(f).convert('RGB'));ys,xs=np.where(own==i);ox,oy=s['tileOriginXY'];assert np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]);assert ref(s['hostOutputFile'])['sha256']==s['sha256'];proof.append({'sourceIndex':i,'pixelCount':len(xs),'exactSameWorldNativePixels':True,'hostByteIdentical':True})
assert sum(p['pixelCount'] for p in proof)==16777216
out=T/'candidate/r07_c06-candidate-native-roi-v10.png';owner=T/'candidate/r07_c06-candidate-native-roi-v10-source-index.png';assert not out.exists();Image.fromarray(pix).save(out);Image.fromarray(own).save(owner)
Q=T/'qa/current-v10-native-20261013';qa=A.write_qa(Image.fromarray(pix),ref(out),Q/'internal')
record={**r,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':ref(out),'sourceIndex':ref(owner),'nativeSources':src,'overlays':overlays,'previousRegistry':ref(prev),'pixelProof':{'status':'passed','checkedPixels':16777216,'sources':proof},'internalQa':qa,'status':'saved_successful_repairs_integrated_pending_material_and_west','internalPassed':False,'formalAccepted':False,'remainingDefects':['West cap material rectangle (two unsuccessful attempts, deferred)','c3c4 inherited vertical material seam; grout gap now closed','West native-frame y215 small gap and y727..756 larger gap (deferred after repeated attempts)'],'sourceResampled':False,'blended':False,'recolored':False}
wj(T/'candidate/native-overlays-20261013-v10.json',record)
# Make full current actual-west QA with a same-world proposed west half. No west tile file is changed.
W=Z/'r07_c05/bridges/shared-east-lower-03/r07_c05-combined-shared-proposal-4096.png';w=Image.open(W).convert('RGB');band=Image.new('RGB',(640,4096));band.paste(w.crop((3776,0,4096,4096)),(0,0));band.paste(Image.fromarray(pix).crop((0,0,320,4096)),(320,0))
n=Image.open(M/'native.png').convert('RGB')
for a,b,c,d in [[617,382,627,408],[617,1077,627,1103]]:band.paste(n.crop((a,b,c,d)),(a-627+320,b+2200))
ext=[]
for i in range(4):
    f=Q/f'west-segment{i+1:02}.png';band.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90).save(f);ext.append(ref(f))
for i in range(1,4):
    f=Q/f'west-junction-{i*1024}.png';band.crop((160,i*1024-160,480,i*1024+160)).save(f);ext.append(ref(f))
wj(Q/'west-proposed-pair-inputs.json',{'westBase':ref(W),'candidate':ref(out),'westMicroSource':ref(M/'native.png'),'westMicroROIs':[[617,382,627,408],[617,1077,627,1103]],'westTileOriginXY':[3469,2200],'westFileModified':False,'crops':ext,'nativePixelScale':1,'formalAccepted':False})
# Reuse only individually hash-identical checks from independently reviewed current v07.
old=T/'qa/current-v07-native-20261013/independent-internal-review-restart-20261013.json';prior={e['name']:e for e in rd(old)['entries']};reuse=[];changed=[]
for e in qa:
    name=Path(e['file']).stem;p=prior[name]
    if e['sha256']==p['sha256']:reuse.append({'name':name,**ref(e['file']),'verdict':p['verdict'],'finding':p['finding'],'evidence':ref(old),'cropBytesUnchanged':True})
    else:changed.append({'name':name,**ref(e['file']),'previousVerdict':p['verdict'],'needsCurrentReview':True})
wj(Q/'reuse-and-required-review.json',{'candidate':ref(out),'reusedChecks':reuse,'changedChecks':changed,'formalAccepted':False})
# All north pixels covered by prior north QA are unchanged; preserve that reviewed evidence.
oldN=T/'qa/current-v07-native-20261013/independent-actual-north-review-restart-20261013.json';oldpix=np.array(Image.open(rd(oldN)['candidate']['file']).convert('RGB'));assert np.array_equal(oldpix[:160],pix[:160]);wj(Q/'north-reuse-proof.json',{'candidate':ref(out),'evidence':ref(oldN),'northBandTileLTRB':[0,0,4096,160],'bandExactPixelMatch':True,'allSevenPriorChecksReused':True,'formalAccepted':False})
print(json.dumps({'candidate':ref(out),'nativeSourceCount':len(src),'nativePixelsProven':16777216,'reusedInternal':len(reuse),'changedInternal':changed},ensure_ascii=False))
