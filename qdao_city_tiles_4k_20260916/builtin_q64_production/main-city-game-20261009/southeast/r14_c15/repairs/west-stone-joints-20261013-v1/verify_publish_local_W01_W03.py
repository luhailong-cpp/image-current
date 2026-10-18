from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];S=T.parent
trial=D/'trial-20261013T164845-W01-alpha-v2-W03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,o,replace=False):
 assert replace or not p.exists(),str(p)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def rgb(p):return np.array(Image.open(p).convert('RGB'))
idx=read(trial/'trial-index.json')
assert sha(idx['base']['path'])==idx['base']['sha256']
core=rgb(idx['base']['path']);base=core.copy();union=np.zeros((4096,4096),bool)
steps=[]
for st in idx['steps']:
 assert sha(st['path'])==st['sha256']
 m=read(st['path'])
 for k in ['preparation','request','sourceReceipt','actualNative','savedAlpha','core','context']:
  assert sha(m[k]['path'])==m[k]['sha256'],k
 prep=read(m['preparation']['path']); receipt=read(m['sourceReceipt']['path'])
 assert receipt['actualModel'] is None and receipt['actualQuality'] is None
 assert receipt['savedNative']['sha256']==m['actualNative']['sha256']
 native=rgb(m['actualNative']['path']);assert native.shape==(1254,1254,3)
 nc=m['nativeCrop'];b=m['pasteBoxIn4096'];alpha=np.array(Image.open(m['savedAlpha']['path']).convert('L'))
 support=np.zeros_like(union);support[b[1]:b[3],b[0]:b[2]]=alpha>0
 assert not np.any(support&union) and np.array_equal(core[support],base[support])
 before=core.copy()
 for y in range(alpha.shape[0]):
  for x in range(alpha.shape[1]):
   a=int(alpha[y,x])
   if a:
    core[b[1]+y,b[0]+x]=tuple((int(before[b[1]+y,b[0]+x,c])*(255-a)+int(native[nc[1]+y,nc[0]+x,c])*a+127)//255 for c in range(3))
 assert np.array_equal(core,rgb(m['core']['path']))
 assert np.array_equal(core[~support],before[~support])
 union|=support;steps.append(st)
final=read(idx['steps'][-1]['path']); context=rgb(final['context']['path']);basecontext=rgb(read(idx['steps'][0]['path'])['preparation']['path']) if False else rgb(read(read(idx['steps'][0]['path'])['preparation']['path'])['sourceContext']['path'])
assert np.array_equal(context[115:4211,115:4211],core)
mask=np.zeros(context.shape[:2],bool);mask[115:4211,115:4211]=True
assert np.array_equal(context[~mask],basecontext[~mask])
assert np.array_equal(core[~union],base[~union])
assert np.array_equal(core[:630,:630],base[:630,:630])
assert sha(idx['finalTrial']['path'])=='0e826f6b1630d86ab7f837221e21bb8bf6c53357ff45204719f9b5f92f1a90f8'
rootqa=trial/'root-independent-local-qa-20261013.json'
assert sha(rootqa)=='7b5e71871916943f11b968e082d92d273ace117001eeec4ee12a9c8f4b27a4bf'
for e in read(rootqa)['viewed']:assert sha(e['path'])==e['sha256']
qa16=T/'review/independent-r14_c16-b0fe86100a9c6347/visual-qa.json';q=read(qa16)
for f in q['sourceFiles'].values():assert sha(f['path'])==f['sha256']
for e in q['reviewedEvidence']:assert sha(e['path'])==e['sha256']
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');delivery=D/('publish-verification-'+stamp);delivery.mkdir()
ver={'verifiedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCandidate':idx['finalTrial'],'scalarReplayExact':True,'outsideUnionAlphaExact':True,'contextHaloExact':True,'frozenNW630Exact':True,'steps':steps,'rootQA':info(rootqa),'formalAccepted':False}
dump(delivery/'scalar-replay-verification.json',ver)
# Save historical mutable metadata before pointer update.
for name,path in [('r14c15-progress',T/'progress.json'),('r14c15-latest',T/'candidate/latest-assembly.json'),('r14c16-progress',S/'r14_c16/progress.json')]:shutil.copyfile(path,delivery/(name+'-before.json'))
prior=read(T/'candidate/latest-assembly.json'); assert prior['candidate']['sha256']==idx['base']['sha256']
dest=T/'candidate/r14_c15-4k-west-W01-alpha-v2-W03-20261013-reviewed.png';ctx=T/'candidate/r14_c15-context-4326-west-W01-alpha-v2-W03-20261013-reviewed.png'
assert not dest.exists() and not ctx.exists()
shutil.copyfile(idx['finalTrial']['path'],dest);shutil.copyfile(final['context']['path'],ctx)
assert sha(dest)==idx['finalTrial']['sha256'] and sha(ctx)==final['context']['sha256']
manifest=T/'candidate/r14_c15-west-W01-alpha-v2-W03-20261013-selected-manifest.json'
selected={'schemaVersion':2,'tile':'r14_c15','selectedAtUtc':datetime.now(timezone.utc).isoformat(),'selection':'root_and_worker_local_visual_review_passed_W01_W03','formalAccepted':False,'candidate':info(dest),'context':info(ctx),'priorSelectedManifest':prior['manifest'],'originalBase':idx['base'],'sourceCompositionIndex':info(trial/'trial-index.json'),'exactOrderedCompositions':steps,'replayVerification':info(delivery/'scalar-replay-verification.json'),'workerQA':info(D/'production-checkpoint-20261013-W02-last-W01-alpha-v2.json'),'rootQA':info(rootqa),'internalArtQA':'passed','internalSeamQA':'passed','externalNeighborSeamQA':{'north':'prior_local_joint_repaired_full_review_pending','west':'W01_W03_local_pass_W02_failed_pending_W04_material_pending','east':'passed_against_r14_c16_b0fe_unchanged_east_pixels','south':'pending'},'eastNeighborQA':info(qa16),'selectedNativeRepairJobs':['W01_same_6de_native_reduced_alpha','W03_cb4_native'],'rejectedNativeRepairJobs':['W02_581542e1','W02_last_v2_23547478'],'newNativeOutputCountInWestBatch':4,'selectedNativeOutputCountInWestBatch':2,'RGBColorCorrection':False,'resampling':False,'allOldImagesRetained':True}
dump(manifest,selected)
p=read(T/'progress.json');p.update(status='internal_pass_west_W01_W03_repaired_W02_failed_pending',updatedAt=datetime.now(timezone.utc).isoformat(),currentVersion='west-W01-alpha-v2-W03-20261013',candidate=str(dest),context=str(ctx),assemblyManifest=str(manifest),internalArtQA='passed',internalSeamQA='passed',externalNeighborSeamQA='north_local_repair_full_pending_west_W02_failed_W04_pending_east_pass_south_pending',formalAccepted=False,rootLatestRepairQA=info(rootqa),workerLatestRepairQA=selected['workerQA'],newWestRepairBatch={'actualNativeOutputCount':4,'selectedNativeOutputCount':2,'W02Attempts':2,'W02Status':'failed_pending_no_more_retry_this_round'},nextStep='Keep W02 failed after two unsuccessful native repairs; revisit with independent later batch. W04 material remains pending; continue stable independent tiles.')
for f in p.get('externalCoreFindings',[]):
 if f['id'] in ['W01','W03']:f.update(currentStatus='locally_repaired_passed',resolvedBy=info(manifest))
 if f['id']=='W02':f.update(currentStatus='failed_pending',attemptCountThisBatch=2,retryDeferred=True,latestFailedNative=info(D/'W02-last-v2/actual-native-235474785ebedb0e.png'))
 if f['id']=='W04':f.update(currentStatus='material_pending')
dump(T/'progress.json',p,True)
latest={'schemaVersion':2,'tile':'r14_c15','status':p['status'],'candidate':info(dest),'context':info(ctx),'manifest':info(manifest),'internalArtQA':'passed','internalSeamQA':'passed','externalNeighborSeamQA':p['externalNeighborSeamQA'],'rootLatestRepairQA':info(rootqa),'workerLatestRepairQA':selected['workerQA'],'formalAccepted':False}
dump(T/'candidate/latest-assembly.json',latest,True)
p16=read(S/'r14_c16/progress.json');assert sha(p16['candidate'])==q['sourceFiles']['candidate']['sha256']
p16.update(status='internal_north_west_visual_pass_material_watch_south_pending',updatedAt=datetime.now(timezone.utc).isoformat(),internalArtQA='passed_with_nonblocking_material_watch',internalSeamQA='passed',externalNeighborSeamQA='north_pass_west_pass_east_canvas_boundary_south_pending',independentVisualQA=info(qa16),nonblockingArtFindings=q['findings'],formalAccepted=False,nextStep='Continue r15_c16; preserve nonblocking gold-trim material watch. South neighboring join needs separate current-core check.')
dump(S/'r14_c16/progress.json',p16,True)
dump(delivery/'published-result.json',{'candidate':info(dest),'context':info(ctx),'manifest':info(manifest),'r14c15Progress':info(T/'progress.json'),'r14c15Latest':info(T/'candidate/latest-assembly.json'),'r14c16Progress':info(S/'r14_c16/progress.json'),'r14c16QA':info(qa16),'formalAccepted':False})
print(json.dumps(read(delivery/'published-result.json')))

