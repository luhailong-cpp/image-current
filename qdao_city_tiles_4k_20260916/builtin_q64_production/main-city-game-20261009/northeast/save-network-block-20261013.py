from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent
NOW=datetime.now(timezone.utc).isoformat()
cutoff=datetime(2026,10,13,8,20,tzinfo=timezone.utc).timestamp()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,j): Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
tiles=['r06_c15','r07_c15','r08_c10','r08_c12']
Q=Z/'qa/network-block-20261013';Q.mkdir(parents=True,exist_ok=True)
err='Fatal error: application network permission was revoked'
block={'recordedAtUtc':NOW,'status':'blocked_application_network_permission_revoked','reportedBy':['/root/middle_resume','/root/left_resume','/root/east_resume'],'exactError':err,'newGenerationAttemptedAfterError':False,'networkBypassAttempted':False,'paidApiAllowed':False,'modelHoldRevoked':True,'note':'Current blocker is explicit application network permission error, not image model metadata. All returned images retained. Local provenance/QA may continue. Resume generation only after permission is restored.','rootRepairTargets':[str(Z/'r07_c15/qa/local-repair-20261013/post-target-v1.png'),str(Z/'r07_c15/qa/local-repair-20261013/stair-target-v1.png')]}
records=[];dirs=set();matched=set();new_inventory=[]
for tid in tiles:
    T=Z/tid
    for rf in (T/'receipts').glob('*.receipt.json'):
        if rf.stat().st_mtime<cutoff:continue
        r=read(rf);src=Path(r['sourceOutputPath']);dirs.add(src.parent)
        name=rf.name.removesuffix('.receipt.json')
        dst=T/'native'/(name+'.png')
        if not dst.exists():dst=T/'native/repairs'/(name+'.png')
        if not dst.exists():raise ValueError('Unmirrored receipt: '+str(rf))
        h=sha(src);assert sha(dst)==h,(src,dst)
        with Image.open(dst) as im: assert im.size==(1254,1254) and im.format=='PNG'
        matched.add(str(src.resolve()));sidecar=Path(str(dst)+'.generation.json')
        if not sidecar.exists():
            request=T/'prompts'/(name+'.request.json');payload=read(request)
            rec={'file':str(dst),'sha256':h,'generatedAt':r.get('receivedAt',NOW),'nativeSize':[1254,1254],'format':'PNG','tool':'image_gen','route':'builtin','sourceOutputPath':str(src),'actualModel':None,'actualQuality':None,'prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(request),'evidence':str(rf),'references':[{'file':str(Path(p)),'sha256':sha(p)} for p in payload['referenced_image_paths']],'resized':False,'assetRole':'AI-generated local repair; not an additional selected core','status':'saved_repair_candidate_not_passed'}
            save(sidecar,rec)
        else:assert read(sidecar)['sha256']==h
        records.append({'tile':tid,'native':str(dst),'source':str(src),'sha256':h,'sourceByteMatch':True,'generationRecord':str(sidecar)})
        new_inventory.append({'file':str(dst),'record':str(sidecar),'sha256':h,'dimensions':[1254,1254]})
orphans=[]
for d in dirs:
    for p in d.glob('*.png'):
        if p.stat().st_mtime>=cutoff and str(p.resolve()) not in matched:orphans.append(str(p))
audit={'checkedAtUtc':NOW,'scope':'Only this resumed batch, cutoff 2026-10-13T08:20Z, four production lanes; prior verified history reused','newNativeOutputCount':len(records),'nativeSources':records,'unmirroredRecentOutputFiles':orphans,'issues':[]}
assert not orphans,orphans
save(Q/'source-recovery.json',audit)
block['returnedNativeOutputsSaved']=len(records);block['unmirroredSuccessfulOutputs']=len(orphans)
save(Z/'network-block-20261013.json',block)
M=Z/'r08_c12';mp=read(M/'tile-progress.json')
mbase=M/'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png'
mp.update({'candidate':str(mbase),'candidateSha256':sha(mbase),'completeCandidateCount':1,'assemblyManifest':str(mbase.parent/'assembly.json'),'workingRepairCandidate':str(M/'candidates/r08_c12.m02-south-v1.png'),'workingRepairCandidateSha256':sha(M/'candidates/r08_c12.m02-south-v1.png'),'workingRepairCandidateStatus':'saved_not_fully_reviewed_not_adopted','pendingP2Count':4,'internalPassed4kCount':0})
save(M/'tile-progress.json',mp)
for tid in tiles:
    T=Z/tid;p=read(T/'tile-progress.json');selection=read(T/'selected-native.json')
    exist=[k for k,v in selection.items() if (T/'native'/v).exists()]
    p.update({'selectedCoreCount':len(exist),'remainingCoreCount':16-len(exist),'updatedAt':NOW,'status':'saved_checkpoint_application_network_permission_blocked','generationStopped':True,'inflightGeneration':None,'blocker':str(Z/'network-block-20261013.json'),'unsavedSuccessfulOutputs':0})
    if tid=='r07_c15':
        row=next(a for a in records if a['tile']==tid)
        p['lastSaved']={'file':row['native'],'sha256':row['sha256'],'nativeSize':[1254,1254],'generationRecord':row['generationRecord'],'savedAtUtc':NOW}
    save(T/'tile-progress.json',p)
inv=read(Z/'current-native-inventory.json');byfile={str(Path(x['file']).resolve()):x for x in inv['outputs']}
for x in new_inventory:byfile[str(Path(x['file']).resolve())]=x
inv.update({'updatedAt':NOW,'outputs':list(byfile.values()),'incrementalAudit':str(Q/'source-recovery.json'),'priorHashVerificationReused':True})
save(Z/'current-native-inventory.json',inv)
prog=read(Z/'progress.json')
for row in prog['tiles']:
    tid=row['tile']
    if tid not in tiles:continue
    T=Z/tid;p=read(T/'tile-progress.json')
    row.update({'generatedNativeCount':sum(Path(x['file']).is_relative_to(T) for x in byfile.values()),'selectedCoreCount':p['selectedCoreCount'],'missingCoreCount':p['remainingCoreCount'],'fullyCovered4kCount':int(bool(p.get('candidate')) and p['selectedCoreCount']==16),'internalPassed4kCount':0,'formalAcceptedCount':0,'candidate':p.get('candidate'),'candidateSha256':p.get('candidateSha256'),'workerStatus':p['status'],'nextPatch':p.get('nextPatch')})
total=sum(x['selectedCoreCount'] for x in prog['tiles']);full=sum(x['fullyCovered4kCount'] for x in prog['tiles'])
prog.update({'updatedAt':NOW,'status':'saved_checkpoint_application_network_permission_blocked','generationStopped':True,'newArtworkGenerationAllowed':False,'networkBlock':str(Z/'network-block-20261013.json'),'generatedNativeCount':len(byfile),'generatedNativeInsideTileDirectories':sum(x['generatedNativeCount'] for x in prog['tiles']),'usableSelectedCoreCount':total,'complete4kCandidateCount':full,'fullyCovered4kCount':full,'complete16Core4kCandidateCount':full,'missingFullyCovered4kCount':60-full,'missingNativeCoreCount':60*16-total,'missingNativeTileCount':60-sum(x['selectedCoreCount']==16 for x in prog['tiles']),'completeTilesPendingInternalReviewCount':sum(x['fullyCovered4kCount'] and not x['internalPassed4kCount'] for x in prog['tiles']),'workQueue':str(Z/'work-queue-finish-20261012.json'),'nextStep':'Restore application network permission, then resume missing native cores and saved local P2 repairs. Do not repeat already saved outputs.','priorUserSuppliedAGENTSInstructionsApply':True})
save(Z/'progress.json',prog)
for name in ['production-resume-20261012.json','current-adopted-index-20261012.json']:
    p=read(Z/name);p.update({'updatedAtUtc':NOW,'generationStopped':True,'newArtworkGenerationAllowed':False,'networkBlock':str(Z/'network-block-20261013.json'),'currentCandidateCount':full,'internalPassedCount':prog['internalPassed4kCount'],'remainingNativeCoreCount':60*16-total})
    save(Z/name,p)
header=f"""# 当前断点：应用网络权限错误（2026-10-13）

本轮已保存 {len(records)} 张新的原生输出（含局部返修），逐张核对生成源与项目文件字节一致，无已返回但未归档图片。本区去重目标60块，当前{full}块原生4K候选、8块内部通过；选定核心{total}/960，仍缺{960-total}片。r07_c15/r08_c12已16/16，P2未通过；r08_c10为13/16；r06_c15为11/16。

三个制作子任务返回同一真实错误：{err}。停止新的联网生成，没有绕过权限或启用付费API。当前不是型号停工：免费/内置2.5优先、内置2.0允许的最新规则继续有效。网络权限恢复后，读取network-block-20261013.json与各tile-progress接续，优先r08_c10最后3片及r07_c15已有局部返修目标；不要重复已保存片。r08_c12两个M02返修原图、版本候选和来源已保留，外边界尚未核完，不算通过。4块划拨坐标继续排除。未改共享Git。

本轮来源核对：qa/network-block-20261013/source-recovery.json。以下为历史记录，不覆盖当前断点。

---

"""
hp=Z/'HANDOFF.md';hp.write_text(header+hp.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps({'newOutputsSaved':len(records),'unmirrored':orphans,'selectedCores':total,'fullCandidates':full,'internalPassed':prog['internalPassed4kCount'],'remainingCores':960-total}))
