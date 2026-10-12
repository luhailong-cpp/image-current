from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;O=B/'work-r06_c04/final-v2'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):
 p=Path(p);tmp=p.with_name(p.name+'.root-tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
a=rd(O/'assembly.json');cp=Path(a['candidate']['file']);assert sha(cp)==a['candidate']['sha256'];assert sha(a['sourceIdMap']['file'])==a['sourceIdMap']['sha256']
im=np.asarray(Image.open(cp).convert('RGB'));ids=np.asarray(Image.open(a['sourceIdMap']['file']));assert ids.shape==(4096,4096);box=a['globalCoreBox'];covered=np.zeros(ids.shape,bool);mismatch=0
for s in a['sources']:
 p=Path(s['file']);assert sha(p)==s['sha256'];yy,xx=np.where(ids==s['sourceId'])
 if not len(xx):continue
 g=s['globalNativeBox'];src=np.asarray(Image.open(p).convert('RGB'));sx=xx+box[0]-g[0];sy=yy+box[1]-g[1];assert sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254
 mismatch+=int(np.any(im[yy,xx]!=src[sy,sx],axis=1).sum());covered[yy,xx]=True
 gp=Path(s['generationRecord']);assert sha(gp)==s['generationRecordSha256'];meta=rd(gp)
 for k in ('request','receipt'):assert Path(meta['evidence'][k]).is_file()
 for ref in meta['references']:assert sha(ref['file'])==ref['sha256']
assert mismatch==0 and covered.all()
idx=rd(B/'current-artifacts.json');n=idx['r05_c04'];assert a['northInheritance']['sha256']==sha(B/n['assembly'])
proof={'pixels':16777216,'mismatches':mismatch,'uncovered':int((~covered).sum()),'rootIndependentReplay':True,'sourceRecordReferenceHashesChecked':True};wr(O/'root-replay-proof.json',proof)
qa={'tile':'r06_c04','candidate':{'file':str(cp),'sha256':sha(cp)},'assembly':{'file':str(O/'assembly.json'),'sha256':sha(O/'assembly.json')},'internalAccepted':True,'status':'internal-native-seams-pass-external-pending','reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'coverage':{'cores':16,'verticalSeams':12,'horizontalSeams':12,'junctions':9,'externalNorthSegments':4,'interiorOtherSideSegments':12},'visualEvidence':{'contacts':str(O/'root-qa-contacts/manifest.json'),'contactManifestSha256':sha(O/'root-qa-contacts/manifest.json'),'nativeSeamImages':[str(O/'qa'/f'{direction}-{k}.native.png') for direction in ('vertical-row','horizontal-col') for k in range(1,5)],'display':'All exact contacts and seam strips reviewed at original detail, no resize.'},'notes':['Workbench seat, rails, draped teal cloth, front and rear legs coherent. Right-end repair has no duplicate external leg or clipped join.','Upright wood grain, metal collar and rounded foot continuous. Sand textures vary gradually across ground, without hard geometry discontinuity.','Gray/cyan road curve and slab seams continuous.'], 'nativeProof':proof,'boundaries':{'north':'pass with current r05_c04','west':'neighbor pending','east':'neighbor pending','south':'neighbor pending'},'formalAccepted':False}
wr(O/'root-qa.json',qa)
snapshot=O/'current-artifacts.before-adoption.json'
if not snapshot.exists():wr(snapshot,idx)
idx['r06_c04']={'candidate':cp.relative_to(B).as_posix(),'assembly':(O/'assembly.json').relative_to(B).as_posix(),'qa':(O/'root-qa.json').relative_to(B).as_posix(),'status':'internally-accepted-north-boundary-passed-candidate','formalAccepted':False}
wr(B/'current-artifacts.json',idx)
print(json.dumps({'adopted':'r06_c04','sha256':sha(cp),'proof':proof}))
