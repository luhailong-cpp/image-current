from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
W=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r02_c05');B=W.parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();idx=B/'current-artifacts.json';m=json.loads(idx.read_text());z=m['r02_c04'];cp=B/z['candidate'];ap=B/z['assembly'];west=cp.parent;assert sha(cp)=='45775fa068aad79be89dc161eaab9450c599351cf8cb6d818fdb49c9233a7a69'
record={'readAtUtc':datetime.now(timezone.utc).isoformat(),'rootIndex':str(idx),'rootIndexSHA256':sha(idx),'westCandidate':str(cp),'westCandidateSHA256':sha(cp),'adoptedNormalizedAssembly':str(ap),'adoptedNormalizedAssemblySHA256':sha(ap),'status':z['status'],'formalAccepted':z['formalAccepted'],'nativeHaloJoint':str(west/'joint.context.png'),'nativeHaloJointSHA256':sha(west/'joint.context.png'),'v02East300EqualsCurrentV03':True,'equalityProof':str(west/'unchanged-regions-proof.json'),'equalityProofSHA256':sha(west/'unchanged-regions-proof.json')}
(W/'adopted-west-20261012.json').write_text(json.dumps(record,indent=2),encoding='utf8');(W/'current-artifacts-read-20261012-v01.json').write_text(idx.read_text(),encoding='utf8')
for r in range(1,5):
 p=W/'guides'/f'west-r02_c04-root-adopted-s{r:02d}.native-context.png';Image.open(west/'joint.context.png').crop((3072,(r-1)*1024,4326,(r-1)*1024+1254)).save(p);Path(str(p)+'.derivation.json').write_text(json.dumps({'file':str(p),'sha256':sha(p),'globalNativeBox':[15245,3981+(r-1)*1024,16499,5235+(r-1)*1024],'sourceCandidate':str(cp),'sourceCandidateSHA256':sha(cp),'sourceAssembly':str(ap),'sourceAssemblySHA256':sha(ap),'haloSourceJoint':str(west/'joint.context.png'),'haloSourceJointSHA256':sha(west/'joint.context.png'),'nativeScaleResampled':False,'guideOnly':True},indent=2),encoding='utf8')
t=(W/'production-v4.py').read_text().replace("WEST=B/'work-r02_c04/resume-20261012-v02'","WEST=B/'work-r02_c04/resume-20261012-v03'").replace('west-r02_c04-s','west-r02_c04-root-adopted-s')
t=t.replace("write(W/'receipts'/(n+'.request.json'),req);print", "req['currentAdoptedWest']=read(W/'adopted-west-20261012.json');write(W/'receipts'/(n+'.request.json'),req);print")
(W/'production-v5.py').write_text(t,encoding='utf8');print(json.dumps(record))

