from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;D=T/'repairs/roof-local-details-20261013-v1';P=D/'composed-D'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
now=datetime.now(timezone.utc).isoformat();qa=D/'root-local-visual-qa-20261013.json';Q=read(D/'root-boundary-qa/manifest.json')
write(qa,{'reviewedAtUtc':now,'reviewer':'/root','source':info(P/'candidate-4096.png'),'method':'Direct 1:1 review of all four composed 1254 native local crops, D four surrounding boundary crops, and four south-edge 1024x356 crops. Overview used only for composition.','results':{'A_unapproved_spiral_removed':'pass; plain gold bend and red support restored; adjoining blue eave caps coherent','B_unapproved_shrub_removed':'pass; stone wall edges and surrounding roof preserved','C_left_rib_connection':'pass; continuous gold strip joins peak and lower band','D_right_rib_connection':'pass; blue cap removed; gold strip continuous to peak and lower band','D_native_adoption_expanded':'actual [2180,1610,2804,2704] to include complete geometry through lower band; immutable preparation proposed [2180,1610,2780,2420]; actual crop and alpha recorded in composition','south_edge_for_continuation':'locally coherent; four native crops inspected; adjacent r15c16 still to be generated'},'boundaryEvidence':info(D/'root-boundary-qa/manifest.json'),'allInternalSeams':'pending independent 57-crop review','externalNeighborSeams':'pending independent review','formalAccepted':False})
C=T/'candidate/r14_c16-4k-roof-local-repairs-v1-20261013.png';X=T/'candidate/r14_c16-context-roof-local-repairs-v1-20261013.png'
for s,d in [(P/'candidate-4096.png',C),(P/'context-4326.png',X)]:
 assert not d.exists();shutil.copyfile(s,d);assert info(s)['sha256']==info(d)['sha256']
M=T/'candidate/r14_c16-roof-local-repairs-v1-selected-manifest.json';old=read(T/'candidate/latest-assembly.json')
manifest={'tile':T.name,'selectedAtUtc':now,'candidate':dict(info(C),size=[4096,4096]),'context':dict(info(X),size=[4326,4326]),'baseAssembly':old['manifest'],'composition':info(P/'composition.json'),'priorComposition':info(D/'composed-A-B-C/composition.json'),'localVisualQA':info(qa),'activeLogicalNativeCount':16,'actualBaseNativeVersions':19,'repairNativeSources':4,'actualNativeOutputCount':23,'status':'selected_local_repairs_passed_remaining_seams_pending','internalArtQA':'local_repairs_passed_full_internal_pending','externalNeighborSeamQA':'pending','resized':False,'formalAccepted':False}
write(M,manifest);write(T/'records/latest-assembly-before-roof-repairs-20261013.json',old)
latest={'schemaVersion':1,'tile':T.name,'status':manifest['status'],'candidate':manifest['candidate'],'context':manifest['context'],'manifest':info(M),'formalAccepted':False};(T/'candidate/latest-assembly.json').write_text(json.dumps(latest,indent=2),encoding='utf-8')
p=read(T/'progress.json');p.update({'updatedAt':now,'status':manifest['status'],'candidate':str(C),'context':str(X),'assemblyManifest':str(M),'repairManifest':str(P/'composition.json'),'internalArtQA':manifest['internalArtQA'],'externalNeighborSeamQA':'pending','formalAccepted':False,'actualNativeOutputCount':23,'nextStep':'Independent full internal and north/west review; continue r15c16 against locally reviewed south core'})
(T/'progress.json').write_text(json.dumps(p,indent=2),encoding='utf-8');print(json.dumps({'candidate':info(C),'context':info(X),'manifest':info(M),'QA':info(qa),'formalAccepted':False}))
