import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,shutil
Z=Path(__file__).resolve().parents[1];Q=Z/'qa';N=Z/'native';A=Z/'migration-stair-rebuild-20261011'/'external-references'
A.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return {'path':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
records=[];issues=[];external={}
for rp in sorted(N.glob('*.png.generation.json')):
 if not rp.name.startswith(('r09_c03_','r10_c03_')):continue
 g=read(rp);p=Path(g['file']);assert p.exists() and sha(p)==g['sha256']
 entry={'stem':p.stem,'native':ref(p),'generationRecord':ref(rp)}
 for ext,key in [('.prompt.txt','prompt'),('.request.json','request'),('.receipt.json','receipt')]:
  f=p.with_suffix(ext);assert f.exists();entry[key]=ref(f)
 receipt=read(p.with_suffix('.receipt.json'));m=re.search(r' as (.*?) by default',receipt.get('output_hint',''))
 if m:
  original=Path(m.group(1));entry['returnedOriginalPath']=original.as_posix()
  if original.exists():
   entry['originalExists']=True;entry['originalSha256']=sha(original);entry['nativeMatchesReturnedOriginal']=sha(original)==sha(p);assert entry['nativeMatchesReturnedOriginal']
  else:entry['originalExists']=False
 records.append(entry)
def scan(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k in ['path','file'] and isinstance(x,str):
    p=Path(x)
    if p.is_absolute() and p.suffix.lower() in ['.png','.jpg','.jpeg','.webp'] and p.is_file() and not p.is_relative_to(Z):
     external[p.as_posix()]=p
   else:scan(x)
 elif isinstance(v,list):
  for x in v:scan(x)
scan(read(Z/'references.json'))
for rp in sorted(N.glob('*.json')):
 if rp.name.startswith(('r09_c03_','r10_c03_','r10_c04_')):
  try:scan(read(rp))
  except (ValueError,UnicodeError):pass
mapping=[]
for original,p in external.items():
 h=sha(p);dest=A/(p.stem+'-'+h[:12]+p.suffix.lower())
 if not dest.exists():shutil.copy2(p,dest)
 assert sha(dest)==h
 mapping.append({'originalPath':original,'archived':ref(dest),'role':'Exact copy of required external raster reference; archived for relocation, original references unchanged.'})
handoff=Q/'r09_c03-final-art-handoff-v1.json';h=read(handoff)
current={
 'r09_c03':{'status':'16_of_16_complete_internal39_east5_passed_before_freeze','handoff':ref(handoff),'finalContext':h['finalTile']['context'],'candidate':h['finalTile']['candidate'],'pairTrace':h['trace'],'audit':h['audit'],'canonicalExportDelegatedToRoot':True},
 'r10_c03':{'status':'10_of_16_native_outputs_saved_not_assembled_not_internal_qa','savedPatchIds':[r['stem'].split('r10_c03_')[1] for r in records if r['stem'].startswith('r10_c03_')],'missingPatchIds':['p03_02','p03_01','p04_04','p04_03','p04_02','p04_01'],'resumePoint':'p03_02_v1 has prepared continuity guide and request only; no prompt, no generation submitted. Do not confuse request preparation with an in-flight image call.','preparedRequest':ref(N/'r10_c03_p03_02_v1.request.json'),'preparedGuide':ref(Z/'layout-only/r10_c03_p03_02_v1_continuity.png'),'productionScript':ref(Q/'r10c03-production-v1.py'),'northAnchor':ref(Q/'pair-r09c03-c04-v1-r09_c03-context-native.png'),'eastAnchor':ref(Q/'block2x2-r09r10c04c05-v1-r10_c04-context-native.png'),'context':None,'trace':None,'candidate':None,'pendingWork':['6 remaining native patches','native assembly','39 internal seam views and any local repair','north/east joining and shared-corner coordination'],'noNewWorkAuthorizedThisTurn':True}}
prior=Q/'r10_c04-sixstep-rebuild-handoff.json'
freeze={'schemaVersion':1,'agent':'/root/stair_rebuild','reason':'User changed objective to commit/push and resume on another computer; parent revoked generation/repair/composition authorization this turn.','stopAcknowledgedAtUtc':'2026-10-12T03:19:10Z','localTimezone':'America/New_York','status':'frozen_for_migration_no_new_generation','inventoryCompletedAtUtc':datetime.now(timezone.utc).isoformat(),'inFlightRequests':[],'inFlightCount':0,'inFlightZeroConfirmed':True,'inFlightEvidence':'All builtin calls in this agent returned completion; no running functions cell remains. Latest submitted generation was r10_c03_p03_03_v1 and its returned original matches archived native. p03_02 is prepare-only.','successfulReturnedOutputsChecked':len(records),'savedR09c03Count':sum(r['stem'].startswith('r09_c03_') for r in records),'savedR10c03Count':sum(r['stem'].startswith('r10_c03_') for r in records),'unsavedSuccessfulOutputs':[],'unsavedSuccessfulCount':0,'outputs':records,'current':current,'priorCompletedStaircaseHandoff':ref(prior) if prior.exists() else None,'externalReferenceArchive':mapping,'relocationNotes':['Archive directory contains exact copies of required external raster references; update reference paths on new machine using originalPath to archived.path mapping without regenerating art.','Preserve entire southwest tree, including native, layout-only, qa, tools, all prompts/requests/receipts/generation records and original candidate/repair versions.','No originals, drafts or previews deleted. No Git writes performed.','r09c03 east pair changes r09c04 western overlap only; future r10c03 join must coordinate shared southwest corner with root.'],'actionsAfterFreeze':['Read local inventory','Verify file hashes and returned-original/native identity','Copy external reference files without image transformation','Write this migration freeze record'],'noNewImageGeneration':True,'noRepairOrCompositionAfterFreeze':True,'noVisualReReviewAfterFreeze':True,'issues':issues}
assert freeze['savedR09c03Count']==16 and freeze['savedR10c03Count']==10
out=Q/'stair_rebuild-migration-freeze-20261011.json';assert not out.exists();out.write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freeze':ref(out),'inFlight':0,'unsavedSuccess':0,'nativeChecked':len(records),'r09c03':16,'r10c03':10,'externalReferencesCopied':len(mapping),'lastSaved':next(r['native'] for r in records if r['stem']=='r10_c03_p03_03_v1')}))

