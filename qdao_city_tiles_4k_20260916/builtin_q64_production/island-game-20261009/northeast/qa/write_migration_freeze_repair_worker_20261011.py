import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import write
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
sp=Z/'selection-r05_c12.json'; s=read(sp)
selected=[]
for row in s['cores']:
 for ident in row:
  if ident:
   p=Z/'native'/f'{ident}.png';g=read(Path(str(p)+'.generation.json'))
   selected.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'recordedSha256':g['sha256'],'hashMatches':sha(p)==g['sha256'],'status':g.get('status'),'coreWorldBox':g.get('coreWorldBox')})
archived=[];external={}; outside={}
for gp in sorted((Z/'native').glob('r05_c12*.png.generation.json')):
 g=read(gp);p=Path(g['file']); ev=g.get('evidence',{}); receipt=ev.get('receipt');prompt=g.get('prompt')
 archived.append({'id':g['id'],'native':p.as_posix(),'sha256':sha(p),'recordedHashMatches':sha(p)==g['sha256'],'generationRecord':gp.as_posix(),'receipt':receipt,'receiptExists':bool(receipt and Path(receipt).exists()),'prompt':prompt,'promptExists':bool(prompt and Path(prompt).exists()),'originalToolPath':ev.get('originalToolPath'),'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality')})
 for ref in g.get('references',[]):
  q=ref.get('file')
  if q and not q.lower().startswith(Z.as_posix().lower()+'/'):
   external[q]={'file':q,'sha256':ref.get('sha256'),'exists':Path(q).exists(),'role':ref.get('role')}
   if not q.lower().startswith('d:/work/image/'):outside[q]=external[q]
last=next(a for a in archived if a['id']=='r05_c12_p02_01')
missing=[f'r05_c12_p{ri+1:02d}_{ci+1:02d}' for ri,row in enumerate(s['cores']) for ci,n in enumerate(row) if n is None]
tile=Z/'tiles'/'r05_c12.png'
pendingGuide=Z/'guides'/'r05_c12_p03_01.anchored-layout-only.png';pendingInputs=Z/'prompts'/'r05_c12_p03_01.inputs.json'
r={'schemaVersion':1,'worker':'repair_prepare_local','state':'frozen_for_user_migration_do_not_resume_without_user','stoppedAtUtc':datetime.now(timezone.utc).isoformat(),'inFlightImagegenCount':0,'returnedUnarchivedUniqueOutputs':[],'lastReturnedAndArchived':last,'selection':{'file':sp.as_posix(),'sha256':sha(sp),'snapshot':s,'filledCoreCount':len(selected),'passedCoreCountBeforeFreeze':12,'provisionalCoreCount':2,'missingCoreCount':len(missing)},'selectedNativeFiles':selected,'tile':{'file':tile.as_posix(),'exists':tile.exists(),'sha256':sha(tile) if tile.exists() else None,'assembled':False},'missingNativeCoreIds':missing,'preparedButNeverSubmitted':{'id':'r05_c12_p03_01','guide':pendingGuide.as_posix(),'guideSha256':sha(pendingGuide),'inputs':pendingInputs.as_posix(),'inputsSha256':sha(pendingInputs),'promptWritten':False,'imagegenSubmitted':False},'pendingRepairs':[{'ids':['r05_c12_p03_02','r05_c12_p04_02_v2'],'issue':'p03_02 native x1024 interior has wrong stair levels and rectangular cream foundation cutoff; p04_02 upper-right continuation inherits stair conflict. Both selected provisionally and NOT passed.','approximateTileLocalFaultX':1933,'approximateTileLocalYRange':[2060,3300],'suggestedNextActionOnlyAfterResume':'Center cross-boundary native repair on c02/c03 internal seam; may need two 1024-core patches across upper stairs and lower continuation. Preserve surrounding cores.'},{'overlayId':'r05_c13_cross_left_p01_beam_repair-r05_c12','issue':'Available shared beam repair reviewed by southeast worker, not yet independently checked or added to c12 selection.','record':(Z/'qa'/'r05_c13_cross_left_p01_beam_repair-r05_c12.overlay.json').as_posix(),'nativeSha256':'1401bb15000d87b6c8d82001fa5e0d549a221d22c92f71ee208e5bb80183fd9b','coreCrop':[115,115,627,1139],'tileLocalPaste':[3584,0]}],'otherRemainingWork':['After missing 2 cores and native repairs, assemble16 cores plus shared overlay using mechanical crop/paste only.','Full tile49crop review and exterior upper/right boundary validation remain pending.','No formal acceptance or global progress update performed by this worker.'],'allR05c12ArchivedGenerations':archived,'referencesOutsideNortheastMustPreserve':list(external.values()),'requiredUniqueReferencesOutsideDWorkImage':list(outside.values()),'outsideWorkspaceGeneratedOriginals':{'mustCarryUniqueFiles':[],'reason':'Original C:/Users/luyua/.codex/generated_images outputs are copied into northeast/native with recorded hashes and receipts; original paths retained in generation metadata.'},'completedEarlierWorkerRecords':['qa/color-repairs-20261011-merge.json','qa/r03_c12-color-repairs-20261011-review.json','qa/r03_c13-color-repairs-20261011-review.json'],'prohibitionsAtFreeze':['no new imagegen','no new repair','no QA long re-review','no new assembly','no Git or deletion','no global progress modification']}
out=Z/'qa'/'migration-freeze-repair-worker-20261011.json';write(out,r)
print(json.dumps({'file':out.as_posix(),'sha256':sha(out),'stoppedAtUtc':r['stoppedAtUtc'],'inFlight':0,'unarchived':[],'filled':len(selected),'passed':12,'provisional':2,'missing':missing,'tileExists':tile.exists(),'lastNative':last['id'],'lastSha256':last['sha256'],'archivedGenerationCount':len(archived),'allArchivePartsExist':all(a['recordedHashMatches'] and a['receiptExists'] and a['promptExists'] for a in archived),'selectionSha256':sha(sp),'externalReferences':list(external.values()),'outsideWorkspaceRequired':list(outside.values())},ensure_ascii=False))
