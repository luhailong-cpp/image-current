from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
T=Path(__file__).resolve().parent;R=T/'repairs-resume-20261012';Q=R/'local-qa';C=T/'candidate'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();resume=read(T/'production-resume-20261012.json');base=resume['baseline']
cm=read(Q/'trial-north-calibrated-and-stone-v2.json');tm=read(cm['parentManifest']['path'])
for k in ('candidate','context','manifest'):assert sha(base[k]['path'])==base[k]['sha256']
assert sha(cm['northSource']['path'])==cm['northSource']['sha256']=='f1d683133fa23f466621f492375b55848d2a8c5775e039f10c2c86bc3860fda5'
arr=np.asarray(Image.open(base['candidate']['path']).convert('RGB')).copy();basearr=arr.copy();allowed=np.zeros(arr.shape[:2],bool)
for op in tm['operations']:
 src=op['source'];assert sha(src['path'])==src['sha256'];assert sha(op['mask']['path'])==op['mask']['sha256']
 prep=read(src['preparation']['path']);assert sha(src['preparation']['path'])==src['preparation']['sha256'];assert sha(src['receipt']['path'])==src['receipt']['sha256']
 for item in [prep['request'],prep['prompt'],prep['target']]+prep['references']:assert sha(item['path'])==item['sha256']
 im=Image.open(src['path']);assert im.size==(1254,1254)
 piece=np.asarray(im.convert('RGB').crop(op['sourceCrop'])).astype(np.uint32);a=np.asarray(Image.open(op['mask']['path'])).astype(np.uint32);h,w=a.shape;x,y=op['targetXY']
 arr[y:y+h,x:x+w]=((piece*a[:,:,None]+arr[y:y+h,x:x+w].astype(np.uint32)*(255-a[:,:,None])+127)//255).astype('uint8');allowed[y:y+h,x:x+w]|=a>0
assert np.array_equal(arr,np.asarray(Image.open(tm['trial']['path']).convert('RGB')))
assert sha(cm['field']['path'])==cm['field']['sha256'];field=np.load(cm['field']['path']);h,w=field.shape[:2]
arr[:h,:w]=np.rint(np.clip(arr[:h,:w].astype(float)+field,0,255)).astype('uint8');allowed[:h,:w]|=np.any(field!=0,axis=2)
assert np.array_equal(arr,np.asarray(Image.open(cm['trial']['path']).convert('RGB')))
assert np.array_equal(arr[~allowed],basearr[~allowed]);ys,xs=np.where(np.any(arr!=basearr,axis=2))
candidate=C/'r15_c13-4k-resume-v2-20261012.png';context=C/'r15_c13-context-4326-resume-v2-20261012.png';manifest=C/'r15_c13-resume-v2-20261012-manifest.json'
for p in (candidate,context,manifest):assert not p.exists(),p
shutil.copy2(cm['trial']['path'],candidate);ct=Image.open(base['context']['path']).convert('RGB');ct.paste(Image.fromarray(arr),(115,115));ct.save(context)
ctarr=np.asarray(ct);origct=np.asarray(Image.open(base['context']['path']).convert('RGB'));halo=np.ones((4326,4326),bool);halo[115:4211,115:4211]=False
assert np.array_equal(ctarr[halo],origct[halo]);assert np.array_equal(ctarr[115:4211,115:4211],arr)
verification={'tile':'r15_c13','verifiedAt':now,'status':'pass','independentIntegerAlphaReplay':True,'float32FieldReplay':True,'replayCoreExact':True,'replayContextCoreExact':True,'contextHaloUnchanged':True,'outsideRepairMasksUnchanged':True,'immutableNorthHashUnchanged':True,'newNativeCount':len(resume['newOutputs']),'nativeActualOutputCount':resume['actualNativeCount'],'allNewSourcesNative1254':True,'allSourceRequestPromptReferenceReceiptHashesVerified':True,'resizeOrWarpApplied':False,'changedPixelBoundingBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedPixelCount':int(len(xs)),'candidate':info(candidate),'context':info(context)}
vp=Q/'resume-v2-verification.json';write(vp,verification)
evidence=[info(Q/('calibrated-north-quarter-'+str(i)+'.png')) for i in range(1,5)]+[info(Q/'stone-relief-v2-trial-detail.png')]
remaining=[{'id':'north-independent-joint-review','status':'pending_independent_acceptance','tileBox':[0,0,4096,354],'description':'All four native north join quarters reviewed locally: contour continuity retained and straight material/value band removed by real native repairs plus recorded photometric stitching. Root should independently confirm, particularly the fine wood-grain transition at x0..70,y0..50; this is not marked formally accepted.'},{'id':'other-neighbor-joints','status':'not_joint_reviewed','edges':['east','south','west'],'description':'Historical standalone edge review retained; current adjacent candidates still required for final joint acceptance.'}]
qa={'tile':'r15_c13','reviewedAt':now,'reviewType':'local_repair_only_no_repeat_of_passed_internal_structure','candidate':info(candidate),'north':'local_visual_improvement_pass_pending_independent_joint_acceptance','stoneRelief':'local_visual_pass_continuous_closed_inset_border','previousInternalStructure':'carried_forward_pass_unchanged_outside_allowed_repairs','formalAccepted':False,'evidence':evidence,'remainingQA':remaining,'photometricStitchingDisclosed':True,'notes':['Three generated northern repair sources were cropped without scaling; alpha masks and one saved RGB harmonic correction field are part of replay. The correction adjusts seam illumination; it does not synthesize material or warp geometry.','Stone mask covers the existing upper inset border and its right return. Handrail cap, post, paving and all pixels outside masks are unchanged.','Immutable north tile r14_c13 v6 was only read.']}
qp=Q/'resume-v2-visual-qa.json';write(qp,qa)
man={'schemaVersion':1,'tile':'r15_c13','version':'resume-v2-20261012','createdAt':now,'status':'candidate_local_repairs_pass_pending_neighbor_acceptance','baseAssembly':base,'repairOperations':tm['operations'],'photometricStitching':cm,'candidate':{**info(candidate),'size':[4096,4096]},'context':{**info(context),'size':[4326,4326]},'verification':info(vp),'visualQA':info(qp),'actualNativeOutputCount':resume['actualNativeCount'],'activeBaseNativeCount':16,'activeRepairNativeCount':4,'immutableNorth':cm['northSource'],'formalAccepted':False,'remainingQA':remaining,'replayScript':info(Path(__file__))}
write(manifest,man)
latest={'schemaVersion':2,'tile':'r15_c13','status':man['status'],'manifest':info(manifest),'candidate':man['candidate'],'context':man['context'],'formalAccepted':False,'internalArtQA':'structural_pass_carried_forward_and_stone_finish_local_pass','externalNeighborSeamQA':'north_local_pass_pending_independent; east_south_west_joint_pending','visualQA':info(qp),'verification':info(vp),'nativeActualOutputCount':resume['actualNativeCount'],'activeNativeCount':16,'activeRepairNativeCount':4,'remainingQA':remaining,'selectionReason':'Four real native repair outputs applied, local QA and independent pixel replay verified.'}
write(C/'selection-20261012.json',latest);write(C/'latest-assembly.json',latest)
progress=read(T/'progress.json');progress.update({'status':latest['status'],'updatedAt':now,'candidate':str(candidate),'context':str(context),'assemblyManifest':str(manifest),'currentVersion':'resume-v2-20261012','nativeActualOutputCount':resume['actualNativeCount'],'activeRepairNativeCount':4,'formalAccepted':False,'internalArtQA':latest['internalArtQA'],'externalNeighborSeamQA':latest['externalNeighborSeamQA'],'visualQA':info(qp),'verification':info(vp),'remainingQA':remaining,'nextStep':'Independent north joint acceptance, then current east/south/west neighboring joints when available.'});write(T/'progress.json',progress)
resume.update({'status':'v2_published_local_repairs_pass_pending_neighbor_acceptance','updatedAt':now,'appliedRepairIds':[op['id'] for op in tm['operations']],'selection':latest,'candidate':man['candidate'],'context':man['context'],'manifest':info(manifest),'verification':info(vp),'visualQA':info(qp),'remainingQA':remaining,'networkError':None,'northCoreUnchanged':True,'photometricStitching':cm['field'],'historicalFreezeModified':False});write(T/'production-resume-20261012.json',resume)
handoff={'tile':'r15_c13','updatedAt':now,'currentSelection':latest,'resumeRecord':info(T/'production-resume-20261012.json'),'newOutputs':resume['newOutputs'],'appliedRepairIds':resume['appliedRepairIds'],'allOriginalsPreserved':True,'gitInvoked':False,'zoneProgressModified':False,'oldFreezeOrAuditModified':False,'immutableNorth':cm['northSource'],'remainingQA':remaining,'nextStep':progress['nextStep']}
write(T/'handoff-r15_c13-20261012.json',handoff);write(T/'local-continuation-20261012.json',handoff)
print(json.dumps({'candidate':man['candidate'],'context':man['context'],'manifest':info(manifest),'verification':verification,'remainingQA':remaining},ensure_ascii=False,indent=2))
