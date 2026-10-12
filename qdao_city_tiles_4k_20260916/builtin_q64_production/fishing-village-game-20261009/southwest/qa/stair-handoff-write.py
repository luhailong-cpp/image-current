import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent;D=Z/'stair-rebuild';Q=Z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
a=read(D/'full-tile-r10_c04-assembly.json');v1=read(Q/'repair-r10_c04-sixstep-v1-qa-manifest.json');v2=read(Q/'repair-r10_c04-sixstep-v2-qa-manifest.json');v4=read(Q/'repair-r10_c04-sixstep-v4-qa-manifest.json')
records=[]
for p in sorted(D.glob('*.png.generation.json')):
 r=read(p);f=Path(r['file']);assert ref(f)['sha256']==r['sha256']
 for inp in r['references']:assert ref(Path(inp['path']))['sha256']==inp['sha256']
 records.append({'record':ref(p),'image':ref(f),'statusAtGeneration':r['status'],'actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality')})
for s in a['sources']:
 assert ref(Path(s['path']))['sha256']==s['sha256'];assert ref(Path(s['record']))['sha256']==s['recordSha256']
checks=[]
for i,e in enumerate(v4['qa'][:39]):
 name=Path(e['file']).name
 if e['sha256']!=v2['qa'][i]['sha256']:basis='Actually viewed v4 native crop after final roadjoin repair';reviewer='stair_rebuild'
 elif '-h' in name:
  basis='Root viewed v1 horizontal set and all seven changed v2 crops; resolved findings then confirmed visually; identical SHA to reviewed v2 crop';reviewer='root'
 else:basis='Stair owner viewed entire v1 vertical/intersection set and all changed v2 crops; identical SHA to reviewed v2 crop';reviewer='stair_rebuild'
 checks.append({**e,'status':'pass_internal_seam','reviewer':reviewer,'reviewBasis':basis})
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r10_c04','status':'internal_native_qa_pass_external_joins_pending','qaCount':39,'checks':checks,'localRepairBoundaryQA':{'leftend':'passed whole native 1254 source/candidate view in v1; unchanged in v2/v4','topnose':'passed whole native 1254 after crop in v2; unchanged in v4','footroad':'v2 stair foot and initial stubs fixed; new right mask stub repaired in v4 roadjoin','lantern':'passed whole native 1254 after crop in v2, uninterrupted red body and wooden grain; unchanged in v4','roadjoin':'passed whole native 1254 after crop in v4 and all four affected seam/intersection crops'},'wholeFlight':'6 continuous noses including top platform nose, stable endpoints, no added seventh riser. Whole 4096 preview viewed at tool-fit size; native crops establish pixel-level quality.','rootHorizontalInitialAudit':ref(Q/'repair-r10_c04-sixstep-v1-root-horizontal-audit.json'),'unresolvedInternalFindings':[],'externalJoinsVerified':False}
ap=Q/'r10_c04-sixstep-rebuild-internal-audit.json';ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
h={'createdAtUtc':audit['createdAtUtc'],'tile':'r10_c04','status':'native_candidate_ready_for_parent_2x2_join','candidate':ref(Q/'repair-r10_c04-sixstep-v4-candidate-4096.png'),'context':ref(Q/'repair-r10_c04-sixstep-v4-context-native.png'),'globalCoreBox':[12288,36864,16384,40960],'globalContextBox':[12173,36749,16499,41075],'coreCropFromContext':[115,115,4211,4211],'internalQA':ref(ap),'qaManifest':ref(Q/'repair-r10_c04-sixstep-v4-qa-manifest.json'),'provenanceChain':[ref(D/'full-tile-r10_c04-assembly.json'),ref(Q/'repair-r10_c04-sixstep-v2-trace.json'),ref(Q/'repair-r10_c04-sixstep-v4-trace.json')],'selectedGridSources':a['sources'],'selectedLocalRepairs':['r10_c04_sixstep_leftend_v1','r10_c04_sixstep_topnose_v1','r10_c04_sixstep_footroad_v1','r10_c04_sixstep_lantern_v1','r10_c04_sixstep_roadjoin_v1'],'generationCounts':{'selectedNewNativeGridPatches':10,'selectedNativeLocalRepairs':5,'rejectedNewGridAttempts':3,'layoutOnlyStructureReference':1,'totalNewBuiltinGenerationFiles':19},'generationRecords':records,'nativeNoUpscale':True,'noFeatherNoColourCorrection':True,'actualModel':None,'actualQuality':None,'modelQualityReason':'Builtin tool neither exposes selection nor returns actual version/quality evidence. No API route used.','structureGuideNeverUsedAsFinalPixels':True,'externalJoinsOwner':'root; unified 2x2 with current topJoint and r10c05','externalJoinsVerified':False,'formalAccepted':False,'doNotSelect':['v1 and v2 superseded by v4','v3 incomplete composition: wrapper lacked globalCoreBox; no complete trace; v4 recomposed correctly','r10_c04_p01_03_v3','r10_c04_p02_04_v2','r10_c04_p03_03_v2']}
p=Q/'r10_c04-sixstep-rebuild-handoff.json';p.write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'handoff':ref(p),'audit':ref(ap),'internalQA':39,'generations':len(records),'sourcesValidated':16}))

