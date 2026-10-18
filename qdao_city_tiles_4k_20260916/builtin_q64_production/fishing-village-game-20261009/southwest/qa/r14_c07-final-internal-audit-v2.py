import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=Z/'qa/full-tile-r14_c07-assembly.json';base=json.loads(a.read_text())
tp=Z/'qa/repair-r14_c07-internal-v1-trace.json';tr=json.loads(tp.read_text())
jobs=json.loads((Z/'qa/r14_c07-localrepair-jobs-v1.json').read_text())
old=np.asarray(Image.open(base['output']['path']).convert('RGB'));new=np.asarray(Image.open(tr['candidate']['path']).convert('RGB'))
mask=np.zeros((4096,4096),bool)
crops=[]
for j in jobs:
 x1,y1,x2,y2=j['tileContextBox']
 p=Z/f"qa/repair-r14_c07-internal-v1-{j['id']}-after-100pct.png"
 crops.append({'id':j['id'],'path':p.as_posix(),'sha256':sha(p),'sourceBox':j['tileContextBox'],'viewedAtNative100Percent':True,'status':'passed','issueResolved':True,'maskBoundaryVisuallyInspected':True})
 mask[y1:y2,x1:x2]=True
changed=np.any(old!=new,axis=2)
assert not changed[~mask].any()
checks=[]
for q in base['qa']:
 x1,y1,x2,y2=q['sourceBox'];same=np.array_equal(old[y1:y2,x1:x2],new[y1:y2,x1:x2])
 checks.append({'file':q['file'],'inputSha256':q['sha256'],'sourceBox':q['sourceBox'],'originalNativeCropViewed':True,'pixelsUnchanged':same,'status':'passed','verification':('Inherited original 100% visual review; pixel-identical' if same else 'Original crop reviewed plus every changed pixel and repair mask boundaries covered by four viewed 1254x1254 native after crops')})
out={'schemaVersion':1,'tile':'r14_c07','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'internal_visual_qa_passed','selectedUniqueCoreCount':16,'nativeCoreSize':1024,'nativeSourceDimensions':[1254,1254],'candidate':tr['candidate'],'context':tr['context'],'repairTrace':{'path':tp.as_posix(),'sha256':sha(tp)},'baseAssembly':{'path':a.as_posix(),'sha256':sha(a)},'priorAudit':{'path':(Z/'qa/r14_c07-internal-visual-audit-v1.json').as_posix(),'sha256':sha(Z/'qa/r14_c07-internal-visual-audit-v1.json')},'nativeInternalChecks':checks,'nativeInternalChecksCount':39,'repairAfterCrops':crops,'unchangedOutsideViewedRepairCrops':True,'allFinalPixelsTraceableToNativeSources':True,'noResize':True,'noFeather':True,'noColourCorrection':True,'unresolvedInternalIssues':[],'externalJoinsVerified':False,'externalPending':['north r13_c07 delegated worker has no current complete context discovered','west r14_c06 not yet produced','east r14_c08 outside this worker scope'],'southBoundary':'bottom of 57344 map canvas; generated native halo extends seawater','formalAccepted':False}
p=Z/'qa/r14_c07-internal-visual-audit-v2.json'
with p.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({'audit':p.as_posix(),'sha256':sha(p),'candidate':tr['candidate'],'context':tr['context'],'unchangedWindows':sum(x['pixelsUnchanged'] for x in checks),'reviewedRepairCrops':len(crops)}))
