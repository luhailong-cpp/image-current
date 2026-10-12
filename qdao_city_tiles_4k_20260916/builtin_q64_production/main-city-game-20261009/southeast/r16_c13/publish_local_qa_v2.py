from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ev(p): return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
mp=T/'candidate/r16_c13-orphan-repair-v2-20261013-manifest.json';m=read(mp)
base=read(m['baseManifest']['path'])
q=T/'review/native-orphan-repair-v2';q49=q/'native49';q49.mkdir(exist_ok=True)
candidate=Image.open(m['candidate']['path']).convert('RGB')
regions=[]
for direction in ('vertical','horizontal'):
 for pos in (1024,2048,3072):
  for quarter in range(4):
   a,b=quarter*1024,(quarter+1)*1024
   box=[pos-256,a,pos+256,b] if direction=='vertical' else [a,pos-256,b,pos+256]
   regions.append((f'{direction}-{pos}-quarter{quarter+1}',box,'seam'))
for y in (1024,2048,3072):
 for x in (1024,2048,3072): regions.append((f'junction-{x}-{y}',[x-450,y-450,x+450,y+450],'junction'))
for edge in ('north','south','west','east'):
 for quarter in range(4):
  a,b=quarter*1024,(quarter+1)*1024
  box={'north':[a,0,b,256],'south':[a,3840,b,4096],'west':[0,a,256,b],'east':[3840,a,4096,b]}[edge]
  regions.append((f'edge-{edge}-quarter{quarter+1}',box,'edge'))
assert len(regions)==49
evidence=[]
for label,box,kind in regions:
 p=q49/f'{label}.png'
 if not p.exists(): candidate.crop(box).save(p)
 e=ev(p);e.update(cropBox=box,kind=kind,resized=False);evidence.append(e)
oldfull=T/'review/native-full-qa-v1'
viewed=[ev(p) for p in sorted(oldfull.glob('*.png'))]
viewed += [ev(p) for p in sorted(Path(base['seamPathsAndAlpha']['path']).parent.glob('junction-*-100pct.png'))]
local=[ev(q/n) for n in ['repair-scar-a-after-100pct.png','repair-scar-b-after-100pct.png','repair-crossing-after-100pct.png']]
qa={'schemaVersion':2,'tile':'r16_c13','reviewedAt':now,'candidate':m['candidate'],'context':m['context'],'formalAccepted':False,'internalArtQA':'pass_after_two_native_local_repairs_with_texture_watch','coverage':{'requiredNativeRegions':49,'seamQuarterRegions':24,'junctionRegions':9,'edgeQuarterRegions':16,'savedCurrentCandidateRegions':evidence,'inspectionBasis':'All six complete seams and four edges were visually inspected at native scale in 2048-pixel half-band files; all nine 900-pixel junctions inspected. North join four quarters and three intersections inspected. After repair, the two defect areas and affected crossing were visually inspected again. Remaining pixels verified unchanged. Saved 49 quarter-region crops map the same full coverage; not claiming 49 new independent tool views.'},'previousNativeViews':viewed,'currentLocalViews':local,'resolved':[{'id':'R16C13-J01','positionInCore':[2740,2127,2740,2176],'result':'Removed short upward mortar stub; continuous block above and clean T-junction below retained.'},{'id':'R16C13-J02','positionInCore':[3192,2099,3192,2176],'result':'Removed short upward mortar stub; horizontal course remains continuous.'}],'externalNeighborSeamQA':{'north':'local_pass_with_texture_watch; independent_root_review_pending','west':'pending_missing_r16_c12_neighbor','east':'pending_r16_c14_generation_and_joint_review','south':'canvas_outer_boundary_no_neighbor; painted_edge_checked'},'textureWatch':'Pale limestone has varying fine mineral grain across native sources. No remaining clear shape break or sharp cut line observed; do not equate local QA with whole-region acceptance.','replay':m['replay'],'actualModel':None,'actualQuality':None,'gameRun':False,'worldSize':None,'capacity5000Validated':False}
qap=q/'visual-qa.json';save(qap,qa)
status='internal_pass_north_local_pass_with_texture_watch_external_pending'
ptr={'schemaVersion':2,'tile':'r16_c13','status':status,'publishedAt':now,'candidate':m['candidate'],'context':m['context'],'manifest':ev(mp),'visualQA':ev(qap),'baseAssemblyManifest':m['baseManifest'],'formalAccepted':False,'internalArtQA':qa['internalArtQA'],'externalNeighborSeamQA':qa['externalNeighborSeamQA'],'activeNativeCount':16,'actualNativeOutputCount':19,'activeRepairNativeCount':1,'replay':m['replay']}
save(T/'candidate/latest-assembly.json',ptr);save(T/'candidate/latest-selection.json',ptr)
p=read(T/'progress.json');p.update(updatedAt=now,status=status,candidate=m['candidate']['path'],candidateSha256=m['candidate']['sha256'],context=m['context']['path'],contextSha256=m['context']['sha256'],assemblyManifest=str(mp),repairManifest=str(mp),visualQA=ev(qap),actualNativeOutputCount=19,activeRepairNativeCount=1,internalArtQA=qa['internalArtQA'],externalNeighborSeamQA=qa['externalNeighborSeamQA'],formalAccepted=False,nextStep='Independent north joint review; generate r16_c14 from stable east edge and inspect joined edge. West neighbor absent; south is canvas boundary.')
save(T/'progress.json',p)
c=read(T/'production-resume-20261012.json');c.update(updatedAt=now,activeNativeCount=16,expectedNativeCount=16,actualNativeOutputCount=19,appliedRepairSourceCount=1,status=status,candidate=m['candidate'],context=m['context'],manifest=ev(mp),visualQA=ev(qap),nextPatches=[],missingNativeCount=0,networkError=None,formalAccepted=False,nextStep=p['nextStep']);save(T/'production-resume-20261012.json',c)
continuation={'schemaVersion':1,'resumedAt':now,'currentCoordinate':'r16_c13','localOnlySinceResume':True,'successfulOutputRecovered':m['repairNative'],'recoveredOutputOriginallyGeneratedAt':read(T/'repairs-20261012/two-orphan-joints-v1.tool-receipt.json')['generatedAt'],'firstNewOutputThisRound':None,'actualNativeOutputCount':19,'selected':ptr,'remaining':qa['externalNeighborSeamQA'],'nextCoordinateAssigned':'r16_c14','modelPolicy':'2026-10-13 corrected free/existing2.5 preferred; existingbuiltin2.0 fallback authorized; actualmetadata null','newNetworkError':None,'gitActions':False,'globalProgressWritten':False}
save(T/'local-continuation-20261013.json',continuation)
print(json.dumps({'candidate':m['candidate'],'context':m['context'],'manifest':ev(mp),'visualQA':ev(qap),'sourceCount':19,'status':status},indent=2))
