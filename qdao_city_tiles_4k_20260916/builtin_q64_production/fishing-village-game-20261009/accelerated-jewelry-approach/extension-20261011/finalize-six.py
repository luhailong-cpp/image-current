from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
b=Path(__file__).resolve().parents[1];e=b/'extension-20261011'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(e/'candidate-manifest.json');q=read(e/'root-final-review.json');a=read(e/'provenance-audit.json')
assert q['status']=='PASS_INTERNAL_QA'
assert a['status'] in ['PASS','PASS_PROVENANCE']
assert not a['issues'] and a['selectedCoreCount']==32
assert all(s['sha256']==sha(s['file']) for s in m['sources'])
assert all(s['sha256'] in json.dumps(a) for s in m['sources'] if s['tile'].startswith('r05_')), 'Final candidate hashes must appear in the provenance replay audit'
assert q['candidateSha256']==m['regionCandidate']['sha256']==sha(m['regionCandidate']['file'])
assert all(x['exactPixelPasteVerified'] for x in m['assemblyChecks'])
raw=[p for t in ['r05_c10','r05_c11'] for p in (b/t/'native').glob('p*-v*.png')]
rep_paths=set()
for t in ['r05_c10','r05_c11']:
 for pattern in ['*/native-result.png','*/repair-native.png']:
  rep_paths.update(p.resolve() for p in (b/t/'repairs').glob(pattern))
 for gp in (b/t/'repairs').rglob('*.generation.json'):
  g=read(gp)
  if g.get('file'):rep_paths.add(Path(g['file']).resolve())
rep=sorted(rep_paths)
assert all(Image.open(p).size==(1254,1254) for p in raw+rep)
now=datetime.now(timezone.utc).isoformat()
outer=[{'tile':f'r03_c{c}','edge':'north','neighbor':f'r02_c{c}'} for c in [10,11]]+[{'tile':f'r05_c{c}','edge':'south','neighbor':f'r06_c{c}'} for c in [10,11]]
outer += [{'tile':f'r{r:02}_c{c}','edge':edge,'neighbor':f'r{r:02}_c{n:02}'} for r in [3,4,5] for c,edge,n in [(10,'west',9),(11,'east',12)]]
counts={'selectedCoreCount':96,'extensionSelectedCoreCount':32,'extensionCoreNativeVersionCount':len(raw),'extensionRepairRawCount':len(rep),'extensionRawCount':len(raw)+len(rep),'priorRawCount':71,'rawGeneratedImageCount':71+len(raw)+len(rep),'allRawNativeDimensions1254':True,'allActualModelQualityUnknown':True}
evidence=[{'file':str(p),'sha256':sha(p)} for p in [e/'root-final-review.json',e/'provenance-audit.json',b/'delivery/production-summary.json']]
m.update({'updatedAt':now,'internalAndRegionQA':'reviewed_no_blocking_findings','formalAcceptedCount':0,'exteriorSeamsReviewed':False,'exteriorSeamsPending':outer,'generationCounts':counts,'qaEvidence':evidence})
write(e/'candidate-manifest.json',m)
summary={'updatedAt':now,'status':'production_complete_six_candidates_ready_for_external_seam_review','coordinates':m['coordinates'],'globalPixelBox':m['globalPixelBox'],'tiles':m['sources'],'region':m['regionCandidate'],'preview':{'file':m['preview'],'classification':'downsampled preview only'},'generationCounts':counts,'nativeMethod':'Each4096 tile uses sixteen unscaled1024 cores from measured1254 builtin outputs with115px halo and recorded native local repairs. Region is exact pixel paste.','nativePixelsResized':False,'overviewPixelsUsedInFinal':False,'paidApiUsed':False,'actualModel':None,'actualQuality':None,'formalAcceptedCount':0,'withinRegionSeamsReviewed':True,'exteriorReviewPending':True,'exteriorSeamsPending':outer,'qaEvidence':evidence,'manifest':str(e/'candidate-manifest.json'),'priorFourPreserved':True,'gitOperationsByThisTask':False}
write(e/'production-summary.json',summary)
progress=read(b/'progress.json')
progress.update({'updatedAt':now,'status':summary['status'],'candidateCount':6,'formalAcceptedCount':0,'selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'rawGeneratedImageCount':counts['rawGeneratedImageCount'],'extensionRawGeneratedImageCount':counts['extensionRawCount'],'extensionCoreVersionCount':len(raw),'extensionRepairRawCount':len(rep),'nextCoordinate':None,'nextCoordinates':[],'withinRegionSeamsReviewed':True,'externalRegionSeamsChecked':False,'nextAction':'Review ten exterior neighbor boundaries before formal acceptance.','candidateManifest':str(e/'candidate-manifest.json'),'productionSummary':str(e/'production-summary.json'),'regionCandidate':m['regionCandidate']})
for s in m['sources']:
 progress['tiles'][s['tile']].update({'candidate':s['file'],'candidateSha256':s['sha256'],'dimensions':[4096,4096],'status':'candidate_complete_internal_and_within_region_seams_reviewed','formalAccepted':False,'externalRegionSeamsChecked':False})
write(b/'progress.json',progress)
handoff=read(e/'migration-handoff.json')
handoff.update({'updatedAt':now,'status':summary['status'],'selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'nextCoordinates':[],'currentDeliveryScope':'Six candidates complete, internal region seams reviewed, ten exterior neighbor boundaries pending.','sixTileManifest':str(e/'candidate-manifest.json'),'sixTileProductionSummary':str(e/'production-summary.json'),'regionCandidate':m['regionCandidate'],'rawGeneratedImageCount':counts['rawGeneratedImageCount'],'formalAcceptedCount':0})
write(e/'migration-handoff.json',handoff)
roundfile=b/'continuation-round-20261011.json'
if roundfile.exists():
 rr=read(roundfile);rr.update({'updatedAt':now,'nextCoordinates':[],'status':summary['status'],'extensionDelivery':str(e/'production-summary.json')})
 rr['candidateStatus'].update({'extensionSelectedCores':32,'extensionRawImageCount':counts['extensionRawCount'],'extensionCandidateCount':2,'totalCandidateCount':6,'withinRegionSeamsReviewed':True,'formalAcceptedCount':0})
 write(roundfile,rr)
print(json.dumps({'status':summary['status'],'counts':counts,'externalPairsPending':len(outer)}))

