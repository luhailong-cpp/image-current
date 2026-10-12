import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=R/'qa/full-tile-r09_c04-assembly.json'
trace=R/'qa/repair-r09_c04-v1-trace.json'
audit=R/'qa/repair-r09_c04-v1-internal-visual-audit.json'
source=R/'qa/repair-r09_c04-v1-candidate-4096.png'
assert sha(source)=='1b34b7380156476a918b2b7ba867b5fcffa1cca0039e4ab10ad4d7ad9883b7ea'
out=R/'tiles/r09_c04.png';out.parent.mkdir(exist_ok=True)
shutil.copyfile(source,out)
assert Image.open(out).size==(4096,4096) and sha(out)==sha(source)
sources=read(base)['sources']
prov={'tile':'r09_c04','status':'internal_qa_passed_pending_external_joins','file':out.as_posix(),'sha256':sha(out),'dimensions':[4096,4096],'globalCoreBox':[12288,32768,16384,36864],'nativePixelsResampled':False,'feathering':False,'derivedFrom':{'path':source.as_posix(),'sha256':sha(source)},'baseAssembly':{'path':base.as_posix(),'sha256':sha(base)},'localizedRepairTrace':{'path':trace.as_posix(),'sha256':sha(trace)},'internalVisualAudit':{'path':audit.as_posix(),'sha256':sha(audit)},'sourceCount':{'regularNativeGridPatches':16,'localNativeAiRepairs':2},'actualModel':None,'actualQuality':None,'modelQualityEvidence':'Each original AI image has separate generation record; host does not expose model or quality. Export introduces no generation and inherits source uncertainty.','externalJoinsValidated':False,'formalAccepted':False,'clientMappingValidated':False,'capacity5000Validated':False,'updatedAtUtc':datetime.now(timezone.utc).isoformat()}
write(Path(str(out)+'.provenance.json'),prov)
plan=read(R/'coordinate-plan.json')
tile=next(t for t in plan['tiles'] if t['tile']=='r09_c04')
tile.update({'status':prov['status'],'output':out.as_posix(),'outputSha256':sha(out),'provenance':str(out)+'.provenance.json'})
for p in tile['patches']:
 s=next(s for s in sources if s['patch']==p['id'])
 p.update({'status':'used_in_internally_verified_tile_with_local_repairs','selectedNative':s['path'],'sha256':s['sha256']})
write(R/'coordinate-plan.json',plan)
progress=read(R/'progress.json')
progress.update({'complete4kCount':1,'formalAcceptedCount':0,'usableNativeCount':16,'acceptedLocalRepairNativeCount':2,'internalQaPending':[],'internalCompleteTiles':['r09_c04'],'candidate4kFiles':['tiles/r09_c04.png'],'updatedAtUtc':prov['updatedAtUtc'],'nextStep':'Continue r09_c05 native road geometry correction, assemble and inspect next tile and shared boundary. Remaining zone target is 49 internal complete tiles; external joins are not yet accepted.'})
write(R/'progress.json',progress)
print(json.dumps({'output':str(out),'sha256':sha(out),'internalComplete4k':1,'formalAccepted':0}))
