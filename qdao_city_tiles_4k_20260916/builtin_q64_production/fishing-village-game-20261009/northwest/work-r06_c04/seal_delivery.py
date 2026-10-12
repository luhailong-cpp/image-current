from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
W=Path(__file__).resolve().parent;O=W/'final-v2'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 assert not p.exists()
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
a=read(O/'assembly.json');proof=read(O/'replay-proof.json')
qa={'tile':'r06_c04','reviewer':'sol_north','reviewedAt':datetime.now(timezone.utc).isoformat(),'candidate':a['candidate'],'status':'internal-native-geometry-and-north-join-pass','internalAccepted':True,'coverage':{'cores':16,'verticalSeams':12,'horizontalSeams':12,'junctions':9,'northActualJoinSegments':4,'otherInteriorSides':12},'reviewMethod':'All16cores,24seams,9junctions and4actualnorthjoin crops viewed at native scale. Final-v2 affected workbench area revisited afterrepair; unchanged regions inherited priorvisual review with pixel-equivalence check by root.','notes':['One builtin native bench right-end repair removes disconnected extension plank and duplicate outside leg, retaining actual supportleg.','No whole-scene scale rejected outputs selected. Cropped left timber fragment sharpened in native v03.','Native wood, cloth, sand, roadcurve continuity pass.'],'boundaries':{'north':{'status':'pass','neighbor':'r05_c04','neighborAssembly':a['northInheritance']['assembly'],'neighborAssemblySha256':a['northInheritance']['sha256']},'west':{'status':'interior-pass-external-pending','neighbor':'r06_c03'},'east':{'status':'interior-pass-external-pending','neighbor':'r06_c05'},'south':{'status':'interior-pass-external-pending','neighbor':'r07_c04'}},'nativeProof':proof,'formalAccepted':False,'rootIndependentQA':ref(O/'root-qa.json')}
write(O/'qa.json',qa)
receipts=list((W/'receipts').glob('*.receipt.json'))
d={'tile':'r06_c04','createdAt':datetime.now(timezone.utc).isoformat(),'status':'delivered-internally-accepted-by-root','candidate':a['candidate'],'assembly':ref(O/'assembly.json'),'qa':ref(O/'qa.json'),'rootQA':ref(O/'root-qa.json'),'sourceEvidence':ref(O/'source-evidence.json'),'proof':ref(O/'replay-proof.json'),'nativeSize':[1254,1254],'selectedCoreCount':16,'savedBuiltinReceipts':len(receipts),'selectedUsedSources':len(read(O/'source-evidence.json')['sources']),'rejectedOriginalsPreserved':['r06_c04_s04_s01_v01','r06_c04_s03_s03_v01'],'replacedOriginalsPreserved':['r06_c04_s04_s01_v02'],'newRepairSources':['r06_c04_bench_right_bridge_v01_20261012'],'modelRoute':'builtin image_gen.imagegen; actual model andquality not returned','paidAPIUsed':False,'formalAccepted':False,'rootIndexWrittenByProducer':False,'gitWritesPerformed':False,'allOldVersionsPreserved':True}
write(O/'delivery.json',d)
print(json.dumps(d,ensure_ascii=False))

