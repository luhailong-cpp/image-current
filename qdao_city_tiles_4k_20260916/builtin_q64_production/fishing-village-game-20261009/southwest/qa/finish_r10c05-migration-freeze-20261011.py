import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, shutil
Z=Path(__file__).resolve().parent.parent
QA=Z/'qa'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
 p=Path(p)
 return {'path':p.as_posix(),'exists':p.exists(),'sha256':sha(p) if p.is_file() else None}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
frozen='2026-10-12T03:15:00.6779426Z'
receipts=[];copied=[];missing=[];refs={}
for p in sorted((Z/'native').glob('r10_c07*.receipt.json')):
 stem=p.name.removesuffix('.receipt.json'); r=read(p)
 hint=r.get('result',{}).get('output_hint','')
 match=re.search(r' as (.+?) by default\.',hint)
 source=Path(match.group(1)) if match else None
 dst=Z/'native'/(stem+'.png')
 if not dst.exists() and source is not None and source.is_file():
  shutil.copy2(source,dst);copied.append(ref(dst))
 companions=[Z/'native'/(stem+s) for s in ['.png','.png.generation.json','.request.json','.prompt.txt','.receipt.json']]
 absent=[x.as_posix() for x in companions if not x.is_file()]
 if absent: missing.extend(absent)
 entry={'stem':stem,'receipt':ref(p),'archive':ref(dst),'missingCompanions':absent,'generatedSource':ref(source) if source else None}
 if source and source.is_file() and dst.is_file():entry['archiveMatchesGeneratedSource']=sha(source)==sha(dst)
 if (Z/'native'/(stem+'.request.json')).exists():
  for r in read(Z/'native'/(stem+'.request.json')).get('references',[]): refs[r['path']]=r
 receipts.append(entry)
external=[]
for path,r in sorted(refs.items()):
 p=Path(path)
 if not p.is_relative_to(Z):external.append({**r,'exists':p.exists(),'currentSha256':sha(p) if p.is_file() else None,'withinWorkspace':p.is_relative_to(Path('D:/work/image')),'migrationAction':'Keep this exact workspace reference file; referenced by saved native generation records. Absolute path must be remapped on the destination computer.'})
names=['repair-r10_c07-v2-context-native.png','repair-r10_c07-v2-candidate-4096.png','repair-r10_c07-v2-trace.json','r10_c07-internal-visual-audit-v2.json','block2x2-r09r10c06c07-v1-context-native.png','block2x2-r09r10c06c07-v1-trace.json','block2x2-r09r10c06c07-v1-r10_c07-candidate-4096.png','r10_c07-block2x2.manifest.json','pair-r09c06-c07-current-v1-context-native.png','pair-r09c06-c07-current-v1-trace.json','r10_c07-topjoin.manifest.json','block2x2-r09r10c05c06-v1-r10_c06-context-native.png','block2x2-r09r10c05c06-v1-r09_c06-context-native.png','pair-r09c06-c07-final-v5-r09_c07-context-native.png','r10_c07-prepare.py','r10_c07-neighbor-overrides.json','r10_c07-repair-prepare.py','r10_c07-review-crops.py']
native_pngs=sorted((Z/'native').glob('r10_c07*.png'))
data={'schemaVersion':1,'agent':'/root/finish_r10c05','frozenAtUtc':frozen,'archiveAuditCompletedAtUtc':datetime.now(timezone.utc).isoformat(),'stopReason':'Latest human instruction relayed by root: freeze all art production for commit/push and move to another computer. All prior continuation authorization revoked for this turn.','artProductionFrozen':True,'newArtGenerationAfterFreeze':False,'newArtCompositionAfterFreeze':False,'newVisualReviewAfterFreeze':False,'gitWritesPerformed':False,'allOriginalsDraftsPreviewsPreserved':True,'inFlightRequests':[],'inFlightCount':0,'zeroInFlightConfirmed':True,'inFlightEvidence':'All issued imagegen tool calls returned successfully and were copied/recorded. Last returned generation is localrepair_wood_v2; last compose session 8051 was collected with exit code 0 before freeze. No imagegen, wait cell, or shell composition process remains pending in this agent.','nativePatchCount':len([p for p in native_pngs if re.search(r'_p\d\d_\d\d_v\d+\.png$',p.name)]),'nativeRepairOutputCount':len([p for p in native_pngs if '_localrepair_' in p.name]),'successfulReceiptCount':len(receipts),'receiptsAndSavedOutputs':receipts,'newlyCopiedPreviouslyUnarchivedOutputs':copied,'unsavedOrMissingOutputs':missing,'essentialCurrentFiles':[ref(QA/n) for n in names],'effectiveInternalArt':{'context':ref(QA/'repair-r10_c07-v2-context-native.png'),'candidate':ref(QA/'repair-r10_c07-v2-candidate-4096.png'),'trace':ref(QA/'repair-r10_c07-v2-trace.json'),'audit':ref(QA/'r10_c07-internal-visual-audit-v2.json'),'status':'Internal art passed before freeze; not canonical/exported by this agent.'},'currentJointCandidate':{'context':ref(QA/'block2x2-r09r10c06c07-v1-context-native.png'),'trace':ref(QA/'block2x2-r09r10c06c07-v1-trace.json'),'r10c07Candidate':ref(QA/'block2x2-r09r10c06c07-v1-r10_c07-candidate-4096.png'),'status':'UNAPPROVED; four-block native composite, shared-edge visual review incomplete and issues identified. Do not promote as final.'},'resumeBreakpoint':{'internalQA':'39 base native windows viewed, 10 affected native windows reinspected, 2 complete native repair boundaries and whole candidate viewed before freeze. Curb v2 and wood v2 integrated.','jointWindowsViewedBeforeFreeze':['east-shared-1','east-shared-2','east-shared-3','east-shared-4','east-shared-5','central-junction','south-shared-1','south-shared-2','south-shared-3'],'jointWindowsNotYetViewed':['south-shared-4','south-shared-5','north-shared-1','north-shared-2','north-shared-3','north-shared-4','north-shared-5','west-shared-1','west-shared-2','west-shared-3','west-shared-4','west-shared-5'],'knownJointRepairIssues':['east-shared-3: bronze lamp post has abrupt dark-to-gold tone boundary across north/south join. No repair crop/request generated.','central-junction and south-shared-1: stone joint abruptly terminates near central junction; native local correction needed. No repair crop/request generated.','east-shared-5: stepped/notched stone-joint geometry should be assessed and likely straightened in native local correction; not yet repaired.'],'pendingHaloQA':'Outer halo ends of shared seams not yet separately cropped or reviewed.','r11c07':'Root assigned next, but no r11_c07 request, image, crop, assembly or generation was started; authorization then revoked by freeze.','layoutObservations':['Lamp foot about 350 native pixels above coarse guide; work stool about 500 native pixels right/up from coarse guide; retained coherent single objects without route obstruction, reported to root.']},'essentialExternalReferences':external,'generatedImageSourceMigration':'All successful generated image outputs are archived as native/*.png and hash-compared to their original C:/Users/luyua/.codex/generated_images sources when available. The original generated_images directory is not required to resume this scoped tile once native images and receipts are carried; keep originals on current computer.','keepDirectoryTrees':['southwest/native/r10_c07* (all versions and sidecars)','southwest/qa/*r10_c07* and *r09r10c06c07* and pair-r09c06-c07-current-v1*','southwest/layout-only/r10_c07*','southwest/continuity/*r10_c07* if present','southwest/tools/seam_helpers.py','southwest/production.py','southwest/references.json','all ancestor trace/context paths referenced by current manifests; no cleanup']}
out=QA/'finish_r10c05-migration-freeze-20261011.json'
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freezeManifest':ref(out),'frozenAtUtc':frozen,'receipts':len(receipts),'nativePatches':data['nativePatchCount'],'nativeRepairs':data['nativeRepairOutputCount'],'allArchivesMatchOriginalSources':all(r.get('archiveMatchesGeneratedSource',False) for r in receipts),'missing':missing,'copied':copied,'externalReferenceCount':len(external),'inFlight':0},ensure_ascii=False))
