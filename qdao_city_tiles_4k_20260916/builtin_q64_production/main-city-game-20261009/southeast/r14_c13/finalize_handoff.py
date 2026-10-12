from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
mf=T/'candidate/r14_c13-repaired-v4-manifest.json';m=read(mf)
assert m['exactPixelReplayVerified'] and len(m['steps'])==7
base_count=len(list((T/'native').glob('*.png.generation.json')))
repair_count=len(list((T/'repairs').glob('*-native.png.generation.json')))
assert base_count==21 and repair_count==8
for entry in [m['candidate'],m['context']]:assert sha(entry['path'])==entry['sha256']
core=np.asarray(Image.open(m['candidate']['path']).convert('RGB'));ctx=np.asarray(Image.open(m['context']['path']).convert('RGB'))
assert np.array_equal(core,ctx[115:4211,115:4211])
qa={'tile':'r14_c13','reviewedAt':now,'candidate':m['candidate'],'context':m['context'],'activeNativeCount':16,'generatedBaseNativeCount':base_count,'generatedRepairNativeCount':repair_count,'appliedRepairNativeCount':7,'allGeneratedNativeCount':base_count+repair_count,'activeContributingNativeCount':23,'nativeSize':[1254,1254],'resampledArt':False,'actualModel':None,'actualQuality':None,'internalSeamQA':'passed after full six seam-band and nine-junction visual review; repair perimeters and four micro repairs also reviewed at native resolution','internalArtQA':'pending_north_neighbor_transition_repair','excludedFromInternalPassBoxInTile':[0,0,4096,256],'externalNeighborSeamQA':'north failed, repair required; other external neighbors not formally accepted','formalAccepted':False,'worldSize':None,'clientMappingValidated':False,'capacity5000Validated':False,'remainingFindings':[{'id':'NORTH-FOLIAGE','boxInTile':[0,0,800,200],'finding':'Leaf silhouettes do not connect to existing r13_c13 at y=0. Preserve existing r13 pixels and repair only new r14 side.','evidence':str(T.parent/'review-notes/r14_c13-native-audit-20261010T111127/p01_01-north-boundary-unscaled.png')},{'id':'NORTH-PAVING','boxInTile':[1900,0,2360,200],'finding':'Northern paving has an isolated/missing grout connection around tile x1950,y120 and older source/new tile mismatch around x2048..2300 at y0. Repair as one slab topology with northern neighbor anchor.','evidence':str(T/'review/repaired-v4/vertical-top-x2048-100pct.png')}],'reviewDirectories':[str(T/'review/repaired-v4'),str(T/'review/micro-dp'),str(T/'review/repaired-v2')],'rejectedCompositions':['repaired-v3 limited circular alpha introduced edge breaks; superseded by v4 minimum-error composition'],'rejectedNativeRepairs':['fix-east-paving: shifted slab corners; retained for evidence only'],'notes':['Roof/eave, beams and railing remain partial architecture from layout. Broad right paving stays open.','Seven applied native repairs reconstructed broken geometry; last two use recorded minimum-error alpha paths to avoid clipping the corrected grout.','Base 16 patch assembly passed strict source/hash/reference/guide replay preflight. Seven selected repair compositions passed exact pixel replay.','Current context copies the repaired 4096 core at integer offset115 into original context. External halo remains unreviewed and must not be propagated.']}
qp=T/'review/repaired-v4/visual-qa.json';write(qp,qa)
m.update(internalArtQA=qa['internalArtQA'],internalSeamQA=qa['internalSeamQA'],externalNeighborSeamQA=qa['externalNeighborSeamQA'],visualQA={'path':str(qp),'sha256':sha(qp)},formalAccepted=False)
write(mf,m)
pointer=T/'candidate/latest-assembly.json';original=read(pointer)
backup=T/'candidate/latest-base-assembly.json'
if not backup.exists():write(backup,original)
latest={'schemaVersion':1,'tile':'r14_c13','status':'internal_seams_reviewed_north_transition_repair_required','manifest':{'path':str(mf),'sha256':sha(mf)},'assemblyIdentitySha256':sha(mf),'baseAssembly':m['baseAssemblyPointerSnapshot'],'candidate':m['candidate'],'context':m['context'],'visualQA':m['visualQA'],'formalAccepted':False}
write(pointer,latest)
progress=read(T/'progress.json');progress.update(status=latest['status'],updatedAt=now,activeNativeCount=16,generatedNativeCount=base_count+repair_count,generatedBaseNativeCount=base_count,generatedRepairNativeCount=repair_count,appliedRepairNativeCount=7,internalArtQA=qa['internalArtQA'],internalSeamQA='passed',externalNeighborSeamQA=qa['externalNeighborSeamQA'],candidate=m['candidate']['path'],context=m['context']['path'],assemblyManifest=str(mf),visualQA=str(qp),complete4kCandidateCount=1,missingNativeCount=0,formalAccepted=False,nextStep='Repair north foliage and stone-grout transition against r13_c13 using new r14 pixels only; then review external seams before acceptance')
write(T/'progress.handoff.json',progress)
(T/'progress.handoff.json').replace(T/'progress.json')
write(T/'repairs/latest-composition.json',m['steps'][-1])
print(json.dumps({'candidate':m['candidate'],'context':m['context'],'manifest':str(mf),'visualQA':str(qp),'generatedNativeCount':base_count+repair_count,'internalSeamQA':'passed','internalArtQA':qa['internalArtQA'],'formalAccepted':False}))
