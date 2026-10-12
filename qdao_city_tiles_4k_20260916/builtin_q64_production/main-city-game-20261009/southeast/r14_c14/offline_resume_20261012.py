from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,uuid,importlib.util,sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';D=T/'review/resume-offline-20261012'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def ck(a):assert sha(a['path'])==a['sha256'],a['path']
def put(p,v):
 q=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');q.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8');q.replace(p)
now=datetime.now(timezone.utc).isoformat();freezePath=T.parent/'migration-freeze-20261011.json';freezeArt=art(freezePath);freeze=rd(freezePath);f=next(a for a in freeze['selectedCandidatePaths'] if a['tile']=='r14_c14');current=rd(T/'candidate/latest-assembly.json')
for k,fk in [('candidate','candidate'),('context','context'),('manifest','assemblyManifest')]:
 ck(current[k]);assert current[k]['sha256']==f[fk]['sha256']
ck(f['activeNativeMap'])
comps={}
for p in R.glob('*/composition.json'):
 m=rd(p);comps[m['candidate']['sha256']]=(p,m)
chain=[];h=current['candidate']['sha256']
while h in comps:
 p,m=comps[h];assert p not in [Path(a['manifest']['path']) for a in chain]
 ck(m['candidate']);ck(m['sourceCandidate']);ck(m['compositor'])
 genkey=next((k for k in ['generation','nativeGeneration','nativeGenerationRecord'] if k in m),None)
 gp=m.get(genkey) if genkey else None
 if gp:ck(gp)
 chain.append({'version':p.parent.name,'manifest':art(p),'candidate':m['candidate'],'sourceCandidate':m['sourceCandidate'],'generation':gp,'native':m.get('native'),'compositor':m['compositor']})
 h=m['sourceCandidate']['sha256']
assert h=='afb8859139b8321fbf3f6f96e2fd463de445b40ab2b1489e3226452893df1aed'
inChain={a['version'] for a in chain};passes=[]
for p in R.glob('*/visual-review.json'):
 v=rd(p)
 if v.get('status')=='local_pass':passes.append({'version':p.parent.name,'review':art(p),'alreadyInPublishedChain':p.parent.name in inChain})
assert all(a['alreadyInPublishedChain'] for a in passes)
usedGenerationPaths={a['generation']['path'] for a in chain if a['generation']}
usedNativeHashes={a['native']['sha256'] for a in chain if a.get('native')}
sources=[]
for p in sorted(R.glob('*/generation.json')):
 g=rd(p)
 for k in ['native','originalOutput','receipt','preparation']:ck(g[k])
 assert g['native']['sha256']==g['originalOutput']['sha256']
 used=g['native']['sha256'] in usedNativeHashes or str(p) in usedGenerationPaths
 reviewPath=p.parent/'visual-review.json'
 sources.append({'version':p.parent.name,'generation':art(p),'native':g['native'],'originalOutput':g['originalOutput'],'receipt':g['receipt'],'preparation':g['preparation'],'selectedPixelsUsedInCurrentCandidate':used,'wholeNativeApproved':False,'explicitReview':art(reviewPath) if reviewPath.exists() else None,'disposition':'Documented subset retained in composition chain; unselected pixels are not approved.' if used else 'Unselected or rejected native preserved; no documented local_pass selection available to auto-promote.'})
active=rd(T/'active-native-map.json');assert len(active)==16
for name,version in active.items():
 p=T/'native'/(version+'.png.generation.json');g=rd(p);assert sha(g['file'])==g['sha256']
original=Image.open(T/'candidate/r14_c14-4k-candidate-8ff54f4e9ec7de483b1a.png').convert('RGB');im=Image.open(current['candidate']['path']).convert('RGB');assert np.array_equal(np.array(im.crop((0,0,630,630))),np.array(original.crop((0,0,630,630))))
# Invoke current immutable compositor replay without rewriting any candidate.
spec=importlib.util.spec_from_file_location('offline_replay',T/'west_dark_structure_selection.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);replay=mod.replay('west-lower-complete-joint-v2-20261011')
north=rd(D/'north-core-sources.json')
northReview={'reviewedAt':now,'status':'not_passed','sources':north,'method':'Four unscaled1024x512 core-only joins and four thin native detail crops viewed. No artwork edited. This is external-edge diagnosis only; internal I01-I07 not reaudited.','frozenCorner':{'x':[0,630],'finding':'Horizontal texture/paper/shadow transitions within frozen corner remain separate root responsibility.'},'findings':[{'approxCoreX':[630,1580],'type':'stone material and grout transition','finding':'Horizontal material division remains at y0; diagonal grout near x1450..1540 enters the boundary with a clipped/offset short branch. Requires fresh local structural native repair against actual north core.'},{'approxCoreX':[1580,1940],'type':'wood grain and light discontinuity','finding':'Large wooden post outline remains present, but grain and brightness jump across y0. Preserve oversized post footprint when repairing.'},{'approxCoreX':[2048,3072],'type':'wood beam and pillar material discontinuity','finding':'Horizontal boundary crosses diagonal beam and large posts; grain/light profiles visibly change abruptly at y0. Do not replace partial structure with whole objects.'},{'approxCoreX':[3072,4096],'type':'major wooden ledge and shadow discontinuity','finding':'Long platform front and its broad diagonal shadow are sharply cut at y0; lower ledge/grain does not follow upper shadow edge smoothly. Needs structure plus illumination continuity, not just a global tint.'}],'formalAccepted':False}
put(D/'north-edge-diagnosis.json',northReview)
inventory={'recordedAt':now,'candidate':current['candidate'],'sourceChainBaseSha256':h,'retainedChain':chain,'localPassSelections':passes,'passedButUnmerged':[],'nativeRepairSources':sources,'preparedOnly':[str(p) for p in sorted(R.glob('*/preparation.json')) if not (p.parent/'generation.json').exists()],'countPolicy':'18 historical base natives plus15 real repair generations =33;16active grid patches. Trial compositions are not extra native generations.'}
put(D/'recovery-source-inventory.json',inventory)
west=rd(T/'review/independent-internal-20261011/west-full-edge/final-west-edge-qa.json')
resume={'schemaVersion':1,'tile':'r14_c14','recordedAt':now,'status':'offline_resume_verified_network_revoked','userAuthorization':art(Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')),'currentOperationalInstruction':'Parent/root latest task requires offline reading and mechanical replay only; do not retry image generation or other network calls.','historicalFreeze':freezeArt,'freezeMatching':{'candidate':True,'context':True,'manifest':True,'activeNativeMap':True},'candidate':current['candidate'],'context':current['context'],'manifest':current['manifest'],'activeNativeCount':16,'historicalNativeCount':33,'nativeRepairCount':15,'newNativeOutputAfter20261012Resume':None,'firstActualNewOutputAfterThisResume':None,'internalQA':'Previously passed I01-I07 and6internalbands/9junctions retained; not re-reviewed in this offline round.','internalQARecord':art(T/'review/full-internal-20261011/visual-qa.json'),'replay':replay,'frozenCorner':[0,0,630,630],'frozenCornerUnchanged':True,'westRemaining':{'groutOutsideFrozenCorner':'pass from existing independent QA','material':'fail','majorY':[2540,2880],'moderateY':[[1660,1820],[3480,3760]],'frozenLegacyY':[0,630],'evidence':art(T/'review/independent-internal-20261011/west-full-edge/final-west-edge-qa.json')},'northRemaining':art(D/'north-edge-diagnosis.json'),'sourceInventory':art(D/'recovery-source-inventory.json'),'passedButUnmergedCount':0,'mechanicalMergePerformed':False,'mechanicalMergeReason':'Every explicit local_pass selection is already included in current chain. Unselected native pixels do not have permission to bypass visual QA.','networkErrors':[{'message':'application network permission revoked','classification':'new restoration-round network denial reported by root','evidenceSource':'Parent/root NEW_TASK on2026-10-12 explicitly reported real application network permission revoked and instructed offline-only. No new imagegen call was issued in this offline round.','rawToolReceiptPath':None,'rawToolReceiptUnavailableHere':True,'newOutputProduced':False,'retryPerformedAfterOfflineInstruction':False}],'offlineWorkCompleted':['Verified candidate/context/manifest/active map against immutable final migration freeze.','Replayed final native composition and checked reserved630corner pixel identity.','Inventoried15 real repair sources and11 retained composition layers, all originals preserved.','Diagnosed current north seam against repaired89c0 selected north core, recording old9f512 pointer discrepancy.'],'offlineAvailableNext':['Use recovery-source-inventory for exact source lookup and mechanical replay of the same retained chain.','Prepare precise masks/prompts for west material-only correction preserving passed grout, and north localized structural repair, without new artwork.','Root can coordinate its frozen corner independently; no passed output remains unmerged in this tile.'],'artWorkStillRequired':['Native material continuity correction at west y2540..2880 and two moderate segments once permitted.','Native north grout/wood grain/ledge-shadow correction outside frozen corner once permitted.','Root-coordinated frozen NW corner and final external acceptance.'],'formalAccepted':False,'newArtworkGeneratedThisOfflineRound':False,'gitOperationsPerformed':False,'historicalFreezeModified':False}
put(T/'production-resume-20261012.json',resume)
progress=rd(T/'progress.json');progress.update(updatedAt=now,status='offline_resume_verified_external_not_passed_network_revoked',generatedNativeCount=33,activeNativeCount=16,inFlightImageGenCount=0,externalNeighborSeamQA='not_passed',formalAccepted=False,productionResumeRecord=str(T/'production-resume-20261012.json'),nextStep='Offline handoff complete. No passed-but-unmerged source remains. West material seams and north structural/material seams require future permitted native generation; frozenNW630 remains root-owned.')
put(T/'progress.json',progress)
assert sha(freezePath)==freezeArt['sha256']
print(json.dumps({'resume':art(T/'production-resume-20261012.json'),'candidate':current['candidate'],'chainLayers':len(chain),'localPassSelections':len(passes),'passedButUnmerged':0,'nativeRepairSources':len(sources),'replay':replay,'freezeUnchanged':True},indent=2))

